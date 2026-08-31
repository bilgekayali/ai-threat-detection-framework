# Changelog

All notable changes to this project are documented here. The project follows Semantic
Versioning for the stable surface defined in `COMPATIBILITY.md`.

## 1.0.0 — 2026-08-31 — Stable research reference

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

- owner-authorized `v1.0.0` tag and GitHub Release publication after exact-main-SHA
  gates, with immutable existing tags and fail-closed API/permission handling;
- publication regression tests and a narrowly scoped GitHub release policy.

Package-index publication, container publication, deployment and independent review
are not authorized or established by this release approval.
