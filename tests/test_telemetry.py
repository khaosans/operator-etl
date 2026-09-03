from __future__ import annotations

from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from operator_etl_graph.graph import run_graph
from telemetry.config import initialize_telemetry


def _metric_names(reader: InMemoryMetricReader) -> set[str]:
    data = reader.get_metrics_data()
    names: set[str] = set()
    for resource_metric in data.resource_metrics:
        for scope_metric in resource_metric.scope_metrics:
            for metric in scope_metric.metrics:
                names.add(metric.name)
    return names


def test_run_graph_emits_sanitized_spans_and_metrics(gov_settings) -> None:
    span_exporter = InMemorySpanExporter()
    metric_reader = InMemoryMetricReader()
    initialize_telemetry(force=True, span_exporter=span_exporter, metric_reader=metric_reader)

    result = run_graph(source="public_comments", settings=gov_settings)

    assert result["status"] == "complete"
    spans = span_exporter.get_finished_spans()
    span_names = {item.name for item in spans}
    assert "operator_etl.graph.run" in span_names
    assert "operator_etl.node.ingest" in span_names
    assert "operator_etl.node.pii_gate" in span_names
    assert "operator_etl.node.validate_load" in span_names
    assert "operator_etl.node.build_gold" in span_names
    assert "operator_etl.node.critic" in span_names

    serialized_attrs = " ".join(
        str(value)
        for item in spans
        for value in (item.attributes or {}).values()
    )
    assert "jane.doe@example.com" not in serialized_attrs
    assert "614-555-0199" not in serialized_attrs
    assert "123-45-6789" not in serialized_attrs

    names = _metric_names(metric_reader)
    assert "etl.rows.processed" in names
    assert "etl.rows.quarantined" in names
    assert "etl.pii.detections" in names
    assert "etl.critic.evaluations" in names
