# Acme Pet Vet Provider Intelligence

A fully synthetic provider-intelligence proof that links pet health episodes to associated claim outcomes, then turns the joined record into condition, treatment-pathway, repeat-condition and provider insights with a buyer-verifiable audit chain.

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

- two deterministic synthetic source feeds: pet-health episodes and associated claims
- stable PetId + HealthEpisodeId linkage with match, orphan and duplicate-key checks
- pet-level health timeline joined through provider encounter to claim and paid outcome
- linked-health views for condition frequency/severity, treatment pathways and repeat-condition cohorts
- deterministic synthetic claims across provider types, regions, conditions and complexity
- adjusted cohorts before comparison
- separate price, service-intensity and referral variance reasons
- minimum sample and `insufficient_evidence` state
- per-insight claim drilldown, method/version and review choices
- append-only source + insight audit chain
- neutral observed arithmetic; no savings claim or causal claim

## What production still needs

Approved schemas and data dictionaries, validated clinical adjustment, enterprise access control, durable atomic storage, extraction lineage, veterinary review operations, contestability, fairness testing, model monitoring, and a pre-registered control design for any intervention claim.


## Demo 2: linked pet health + claims

Run `python3 generate.py`, `python3 analyze.py`, and `python3 build_linked_demo.py`. The linked build materializes two distinct synthetic feeds in `docs/`, verifies a one-to-one PetId + HealthEpisodeId join, and publishes `docs/scenario1.html`. `python3 verify.py` checks the full join and both audit chains. All measures are descriptive; the demo makes no causal or savings claim.
