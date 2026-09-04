from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from threading import Lock
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.metrics import Counter, Meter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import MetricReader, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter
from opentelemetry.trace import Tracer

logger = logging.getLogger("operator_etl.telemetry")


def _truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class TelemetryCounters:
    rows_processed: Counter
    rows_quarantined: Counter
    pii_detections: Counter
    critic_evaluations: Counter


@dataclass(frozen=True)
class TelemetryRuntime:
    service_name: str
    endpoint: str | None
    langchain_tracing_v2: bool
    tracer_provider: TracerProvider
    meter_provider: MeterProvider
    meter: Meter
    counters: TelemetryCounters


_LOCK = Lock()
_RUNTIME: TelemetryRuntime | None = None
_LANGCHAIN_INSTRUMENTED = False


def _service_name() -> str:
    return os.getenv("OTEL_SERVICE_NAME", "operator-etl")


def _resource() -> Resource:
    return Resource.create({"service.name": _service_name()})


def _build_tracer_provider(
    endpoint: str | None, span_exporter: SpanExporter | None = None
) -> TracerProvider:
    provider = TracerProvider(resource=_resource())
    if span_exporter is not None:
        provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        return provider
    if endpoint:
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint.rstrip('/')}/v1/traces"))
        )
    return provider


def _build_meter_provider(
    endpoint: str | None, metric_reader: MetricReader | None = None
) -> MeterProvider:
    readers: list[MetricReader] = []
    if metric_reader is not None:
        readers.append(metric_reader)
    elif endpoint:
        exporter = OTLPMetricExporter(endpoint=f"{endpoint.rstrip('/')}/v1/metrics")
        readers.append(PeriodicExportingMetricReader(exporter))
    return MeterProvider(resource=_resource(), metric_readers=readers)


def _build_runtime(
    *,
    endpoint: str | None,
    span_exporter: SpanExporter | None = None,
    metric_reader: MetricReader | None = None,
) -> TelemetryRuntime:
    tracer_provider = _build_tracer_provider(endpoint, span_exporter=span_exporter)
    meter_provider = _build_meter_provider(endpoint, metric_reader=metric_reader)
    try:
        trace.set_tracer_provider(tracer_provider)
    except Exception:
        logger.debug("OpenTelemetry tracer provider already installed")
    try:
        metrics.set_meter_provider(meter_provider)
    except Exception:
        logger.debug("OpenTelemetry meter provider already installed")
    meter = meter_provider.get_meter("operator-etl")
    counters = TelemetryCounters(
        rows_processed=meter.create_counter(
            "etl.rows.processed", unit="rows", description="Rows processed by stage"
        ),
        rows_quarantined=meter.create_counter(
            "etl.rows.quarantined",
            unit="rows",
            description="Rows quarantined by normalized reason",
        ),
        pii_detections=meter.create_counter(
            "etl.pii.detections",
            unit="detections",
            description="PII detections by entity type without raw values",
        ),
        critic_evaluations=meter.create_counter(
            "etl.critic.evaluations",
            unit="evaluations",
            description="Critic pass or fail outcomes",
        ),
    )
    runtime = TelemetryRuntime(
        service_name=_service_name(),
        endpoint=endpoint,
        langchain_tracing_v2=_truthy(os.getenv("LANGCHAIN_TRACING_V2")),
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        meter=meter,
        counters=counters,
    )
    if runtime.langchain_tracing_v2:
        _instrument_langchain(runtime)
    return runtime


def _instrument_langchain(runtime: TelemetryRuntime) -> None:
    global _LANGCHAIN_INSTRUMENTED
    if _LANGCHAIN_INSTRUMENTED:
        return
    try:
        from openinference.instrumentation import TraceConfig
        from openinference.instrumentation.langchain import LangChainInstrumentor

        config = TraceConfig(hide_inputs=True, hide_outputs=True)
        LangChainInstrumentor().instrument(tracer_provider=runtime.tracer_provider, config=config)
        _LANGCHAIN_INSTRUMENTED = True
        return
    except Exception:
        logger.debug("OpenInference TraceConfig instrumentation unavailable")

    try:
        from openinference.instrumentation.langchain import LangChainInstrumentor

        LangChainInstrumentor().instrument(tracer_provider=runtime.tracer_provider)
        _LANGCHAIN_INSTRUMENTED = True
    except Exception:
        return


def initialize_telemetry(
    *,
    force: bool = False,
    span_exporter: SpanExporter | None = None,
    metric_reader: MetricReader | None = None,
) -> TelemetryRuntime:
    global _RUNTIME
    with _LOCK:
        if _RUNTIME is not None and not force:
            return _RUNTIME
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        _RUNTIME = _build_runtime(
            endpoint=endpoint, span_exporter=span_exporter, metric_reader=metric_reader
        )
        return _RUNTIME


def get_runtime() -> TelemetryRuntime:
    return initialize_telemetry()


def get_tracer(name: str = "operator-etl") -> Tracer:
    return get_runtime().tracer_provider.get_tracer(name)


def get_meter() -> Meter:
    return get_runtime().meter_provider.get_meter("operator-etl")


def shutdown_telemetry() -> None:
    runtime = _RUNTIME
    if runtime is None:
        return
    runtime.meter_provider.shutdown()
    runtime.tracer_provider.shutdown()


def telemetry_enabled() -> bool:
    runtime = get_runtime()
    return runtime.endpoint is not None


def safe_attributes(attributes: dict[str, Any] | None = None) -> dict[str, Any]:
    if not attributes:
        return {}
    cleaned: dict[str, Any] = {}
    for key, value in attributes.items():
        if value is None:
            continue
        if isinstance(value, (str, bool, int, float)):
            cleaned[key] = value
        else:
            cleaned[key] = str(value)
    return cleaned
