# Hybrid Document Verification for Research Records

A hybrid verification layer for research documents: a small local LLM drafts and
judges, and a deterministic claim checker verifies every checkable statement
against the underlying evidence record before it is trusted. Everything runs
locally (llama.cpp, CPU only, no network access), so confidential research
records never leave the machine.

Built by LifeAnalytics Inc. for the #BuildHybridAI 2026 hackathon.

## Why hybrid

A bare small model is not reliable enough to verify scientific statements —
and its errors concentrate exactly where they hurt: it lets wrong statements
pass. In our pre-registered benchmark, the bare 3B model missed 55.0% of
dangerous errors in Japanese verification. Adding the deterministic layer —
which mechanically checks every labelled value, direction claim and
significance form against the evidence row for the named entity — brought the
dangerous-miss rate to 0.0% on the same items, with model judgment kept only
as a fallback for statements that carry no parseable checkable claim.

## Measured results (pre-registered protocols, independently recalculated)

All runs: llama.cpp, Qwen2.5-3B-Instruct (GGUF Q4_K_M), temperature 0, CPU only.
Data: Schnell et al. 2025 human kidney organoid RNA-seq (GEO GSE264217),
analysed with DESeq2 1.42.0 and fgsea. Headline metrics were recalculated with
a separate pandas implementation and agreed exactly. See `PILOT_REPORT.md`
for the full report, including 7B results and all benchmark domains
(classification, dose-response QC, microscopy QC and verification).

| Benchmark | Set | Hybrid layer | Bare model (3B) |
|---|---|---|---|
| Verification (EN) | 120 statements | agreement 100%, κ 1.000, dangerous miss 0.0% | 74.2%, κ 0.483, dangerous miss 43.3% |
| Verification (JP) | 120 statements | agreement 100%, κ 1.000, dangerous miss 0.0% | 72.5%, κ 0.450, dangerous miss 55.0% |
| Classification (EN) | 600 cases | agreement 100%, κ 1.000 | 92.5%, κ 0.876 |
| Classification (JP) | 600 cases | agreement 100%, κ 1.000 | 92.8%, κ 0.882 |

## Scope notes (read before citing the numbers)

- Two kinds of result are reported separately in `PILOT_REPORT.md` and must
  not be conflated. Deterministic-decision classes validate that the
  implementation reproduces the pre-registered rule exactly; they are not
  evidence of model capability. Checked-judgment classes validate the claim
  checker against a registered fault taxonomy (flipped direction, wrong-row
  values, significance asserted against the values).
- Free-form claims outside the registered formats remain on a
  model-plus-human-gate path, which this benchmark does not measure.
- The benchmark covers English and Japanese document verification and
  classification of research records. It is not a handwriting or form
  recognition benchmark.

## Repository layout

- `evaluate.py`, `evaluate2.py`, `evaluate_jp.py` — evaluation entry points
- `run_bench_verif.py`, `run_bench_class.py`, `run_domain.py` — benchmark runners
- `build_record.py` — evidence-record construction
- `verify_recalc.py` — independent metric recalculation
- `cases.csv`, `claims.csv`, `claims_jp.csv` — case and claim definitions
- `config.json`, `config_jp.json` — pre-registered run protocols
- `bench_*.csv`, `results_jp.csv`, `metrics.json` — recorded results
- `PILOT_REPORT.md` — full pilot report

## Requirements

- Python 3 with pandas
- llama.cpp with a GGUF model (Qwen2.5-3B-Instruct Q4_K_M used here; model
  files are not included in this repository)

## License

MIT (see `LICENSE`).
