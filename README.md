# Acme Pet Vet Provider Intelligence

A fully synthetic provider-intelligence proof that turns claim episodes into adjusted peer benchmarks, candidate review packets, monthly cost observations, and a buyer-verifiable audit chain.

Acme Pet turns synthetic claim episodes into explainable provider insights. Veterinary reviewers can agree, mark a clinical justification, challenge the cohort or data, or request more evidence before action.

## Run

```bash
python3 generate.py
python3 analyze.py
python3 verify.py
python3 -m http.server 8000 --directory docs
```

Open `http://localhost:8000`.

## What it proves

- deterministic synthetic claims across provider types, regions, conditions and complexity
- adjusted cohorts before comparison
- separate price, service-intensity and referral variance reasons
- minimum sample and `insufficient_evidence` state
- per-insight claim drilldown, method/version and review choices
- append-only source + insight audit chain
- neutral observed arithmetic; no savings claim or causal claim

## What production still needs

Approved schemas and data dictionaries, validated clinical adjustment, enterprise access control, durable atomic storage, extraction lineage, veterinary review operations, contestability, fairness testing, model monitoring, and a pre-registered control design for any intervention claim.
