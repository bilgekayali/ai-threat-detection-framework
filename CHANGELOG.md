# Changelog

All notable changes to this project are documented here. The project follows Semantic
Versioning for the stable surface defined in `COMPATIBILITY.md`.

## 1.0.0 — Stable reference pending explicit tag decision

- formalized the six-symbol public Python API and two-command CLI contract;
- added five Draft 2020-12 schemas for normalized input and evaluation evidence;
- added train/holdout partition labels, Brier score and recorded runtime versions;
- added a deterministic evidence manifest with exact artifact hashes;
- aligned event-type validation with the five documented synthetic event families;
- added model, dataset, threat-model, compatibility and release-process documentation;
- added a frozen release contract and reference-dataset fingerprint;
- added Python 3.10/3.11/3.12 CI, exact GitHub Action pins, CodeQL and a clean-wheel
  stable release gate;
- added deterministic CycloneDX dependency evidence generation;
- preserved explicit non-claims for production performance, readiness, compliance,
  certification and autonomous containment.

No `v1.0.0` tag, GitHub Release, package publication or deployment is created by the
source hardening change.
