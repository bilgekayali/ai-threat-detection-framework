# Threat Model

## Protected properties

The reference implementation is designed to preserve input-contract integrity,
chronological evaluation separation, bounded scores, reproducible configuration,
artifact traceability and explicit human-decision boundaries.

It does not hold credentials, call external services, serialize executable models or
perform response actions.

## Trust boundaries

- Input CSV files are untrusted until schema and range validation succeeds.
- Package code and configuration define the evaluation boundary.
- Generated CSV/JSON files are evidence outputs, not authorization instructions.
- A downstream analyst, case-management system or governance workflow is outside this
  repository and must independently verify provenance and authority.

## Principal threats and controls

| Threat | Reference control |
| --- | --- |
| Missing, malformed or out-of-range input | Fail-closed field, type and range validation |
| Future-to-past leakage | Chronological split and explicit train/holdout labels |
| Silent configuration drift | Configuration and runtime details in the report |
| Artifact substitution | SHA-256 evidence manifest |
| Unsupported event taxonomy | Closed v1 event-type enumeration |
| Misleading performance claims | Synthetic-data limitations and explicit non-claims |
| Autonomous harmful action | No containment integration and human-triage boundary |
| Workflow dependency drift | Exact GitHub Action commit pins |

## Residual risks

SHA-256 manifests do not authenticate the identity of the producer; signed provenance
would be required for a higher-assurance distribution. Dependency compromise, malicious
source changes, spreadsheet formula interpretation, model bias and misuse of synthetic
metrics remain possible. CI and CodeQL reduce some implementation risk but do not prove
the absence of vulnerabilities.

## Out of scope

Production SIEM/XDR/SOAR integration, credential handling, endpoint isolation, account
suspension, legal determinations, certification, institution-specific threat modelling
and live security-control effectiveness are outside this reference implementation.
