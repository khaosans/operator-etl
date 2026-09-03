# Models — which one, and where the data goes

**When to read:** Verify is green on the **template** path and you want a local or cloud model to draft insight *wording*. Install steps: [LLM.md](LLM.md). Risk framing: [NIST.md](NIST.md).

The model is a **wording engine over gold numbers**, not a warehouse analyst. It receives numeric KPI JSON. It never sees bronze rows, comment bodies, or vault PII. That is the NIST **Map** choice: we know exactly what can leave the organizational boundary (cloud) or stay on the laptop (Ollama).

Default remains the **template**. `./scripts/verify.sh` and CI do not call a model. Optional LLM is **PARTIAL** — mocked in CI; a maintainer laptop run of `llama3.2:3b` critic-passed. That is not a production FOIA claim.

## Efficient defaults (cost / tokens)

| Knob | Default | Why |
|---|---|---|
| `OPERATOR_ETL_INSIGHT_BACKEND` | `template` | Zero model calls in CI and staging until you opt in |
| `OPERATOR_ETL_MAX_LLM_CALLS` | `2` | One draft + one retry; FOIA path needs a single completion |
| `OPERATOR_ETL_LLM_MAX_TOKENS` | `256` | Insight is 2–4 sentences — cap completion length |
| LLM gold payload | 5 KPI keys only | `comment_count`, `docket_count`, `agency_count`, `pii_flagged_count`, `pii_rate` — no timestamps or extra mart columns |
| Temperature | `0` | Deterministic wording; critic still validates digits |

Prefer **template** or local **Ollama** for demos. Flip cloud `insight_backend=llm` only with a real secret and after reading [LLM.md](LLM.md).

---

## When to use which

| Path | Use when | Do not use when |
|---|---|---|
| **Template** | First run, CI, no GPU or API key | You need varied prose |
| **Ollama `llama3.2:3b`** | Laptop demo; gold JSON must stay on-box (Map: local) | You need CI proof or production FOIA claims |
| **Cloud `gpt-4o-mini`** | Hosted wording; Cloud Run after a **real** Secret Manager key | Policy forbids gold JSON leaving the box; secret still `REPLACE_ME` |

Other OpenAI-compatible `/v1` servers (LM Studio, vLLM) can speak the same API. They are **untested** in this repo except as a documented pattern. Hugging Face `transformers`, llama.cpp CLI, MLX, and Gemini-native SDKs are **not** supported runtimes here.

---

## What “instruct” and quantization mean

**Base** checkpoints continue pretraining text. **Instruct** (chat) checkpoints are tuned to follow a system prompt — the shape `ChatOpenAI` already sends. Pull `llama3.2:3b` (Instruct via Ollama), not a raw base dump.

Ollama ships a **quantized** GGUF-style build: smaller disk and RAM, slightly lossier than full precision. A 3B-class model is roughly **~2 GB on disk** and comfortable on an **8 GB** machine. 7B-class (e.g. `mistral`) wants more headroom. No discrete GPU is required: Apple Silicon uses Metal; CPU-only works and is slower.

The critic checks that **digits in the draft exist in gold**. It does not check that the sentence used `pii_rate` `0.4` as a rate rather than “40 comments.” Small models misread. Do not loosen the critic. Try `mistral` or stay on the template.

---

## Model cards (summaries — official text is at the links)

We do not copy vendor cards. Facts below are orientation; licenses and evals live on the card.

### Llama 3.2 3B Instruct — `llama3.2:3b`

Meta instruct-tuned text model (~3.2B parameters). Vendor card: multilingual dialogue / summarization, 128k context, knowledge cutoff December 2023. **Proven in this repo:** maintainer laptop against Ollama, critic passed, gold-KPI payload only. **Not** proven in CI.

License: [Llama 3.2 Community License](https://www.llama.com/llama3_2/license/) (you remain bound when you `ollama pull`).

- [Hugging Face model card](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
- [Meta MODEL_CARD.md](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md)
- [Ollama library: llama3.2](https://ollama.com/library/llama3.2)

### Mistral — Ollama tag `mistral`

Suggested **fallback** if 3B garbles rates. **Not** proven in this repository. Start from [Ollama mistral](https://ollama.com/library/mistral) and the upstream Hugging Face card linked there.

### GPT-4o mini — `gpt-4o-mini`

Code and Terraform default for hosted OpenAI. Fast small chat model; we send gold JSON only (text, not images). **Not** live in CI. Gold KPI JSON **leaves the box** to OpenAI.

- [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-4o-mini)
- [GPT-4o system card](https://openai.com/index/gpt-4o-system-card/) — mini is in the 4o family; we do not invent a separate mini system card.

---

## Data boundary (NIST Map)

| Backend | Where gold KPI JSON goes |
|---|---|
| Template | Nowhere — filled in-process |
| Ollama `127.0.0.1:11434` | Stays on the machine |
| OpenAI API (no base URL) | Leaves the machine to OpenAI |
| Cloud Run + Secret Manager | Same as OpenAI once `OPERATOR_ETL_INSIGHT_BACKEND=llm` |

Install and env vars: [LLM.md](LLM.md).
