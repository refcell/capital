---
name: reviewing-research
description: "Reviews a draft research call in the refcell/capital repo as an independent skeptic before it is published: scores fixed dimensions, explains every low score, and writes the strongest counter-case, which the author must answer in call.json. Use when asked to review a call, before committing a research run, or when a run's call.json has no review block."
---

# Reviewing a research call

You are the second reader. You did not write this call and you are not trying to agree with it. Read only what is committed or staged for the call: `data/<T>/<date>/call.json`, `inputs.json`, `sources/`, the report named in `artifacts.report`, and the prior call if `prior_call` is set. Do not edit the report or the numbers.

## Score each dimension from 1 to 5 before giving an overall grade

| Dimension | 5 means | 1 means |
|---|---|---|
| `evidence` | Every number in the scenarios traces to `inputs.json` or a saved source | Key numbers have no source, or sources contradict them |
| `valuation` | Lens fits the business; bear/base/bull follow from stated drivers; weights are defended | Multiples or growth picked to land on a target; weights unexplained |
| `variant_view` | States what the market believes and a specific, checkable disagreement | Restates the consensus or the company's narrative |
| `risk` | Pre-mortem reasons are distinct and each has an early signal; kill criteria are testable | Generic risks; kill criteria that can never fire |
| `calibration` | Scenario growth is plausible against `library/BASE_RATES.md`; claim probabilities are neither all ~50% nor all ~90% | Bull growth above the 90th percentile without evidence; upside of 70%+ treated as likely |

Score first, then write a one-sentence reason for any score of 3 or lower. Then give the overall `grade` (A to D). A grade is not an average: one score of 1 caps the grade at C.

## Write the strongest counter-case

Two to four sentences arguing the opposite stance as well as a good analyst on the other side would. Use the call's own data where possible (for example, a base-case CAGR at the 85th percentile of its size bucket).

## Record it

Add a `review` block to `call.json`:

```json
"review": {
  "reviewer": "agent:reviewing-research",
  "date": "YYYY-MM-DD",
  "scores": {"evidence": 4, "valuation": 3, "variant_view": 3, "risk": 4, "calibration": 3},
  "low_score_reasons": ["valuation: ...", "variant_view: ...", "calibration: ..."],
  "grade": "B",
  "counter_case": "...",
  "response": null
}
```

The author then fills `response`: what changed because of the review, or why nothing did. `python3 -m capital.validate` requires a review with a response on every call written by a run.
