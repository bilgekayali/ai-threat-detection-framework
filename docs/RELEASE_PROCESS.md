# Release Process

Version and publication are separate decisions. The owner explicitly authorized the
v1.0.0 GitHub tag/Release on 2026-08-31. The approval does not establish independent
review and does not authorize a package index, container publication or deployment.

1. Prepare release changes on a non-default branch.
2. Run lint, tests, schema validation, full-dataset evaluation and clean-wheel smoke.
3. Verify the frozen API, schema and dataset with
   `python tools/release_contract.py --emit --verify`.
4. Generate dependency evidence using `python tools/build_sbom.py --output sbom.json`.
5. Require CI, CodeQL and Stable Release Gate success on the exact PR head SHA.
6. Squash-merge the approved head; record any owner review waiver honestly.
7. Require the same three workflows to succeed on the exact current `main` merge SHA.
8. Only then publish the explicitly authorized version in `release/publish-policy.json`.

## Enforced publication gate

`Publish release` listens to completion of the three required workflows. Its first
job is read-only. `tools/publish_release.py` binds the repository, workflow paths and
names, push event, `main` branch and full 40-character SHA; it reads all run pages and
requires the latest attempt of every gate to succeed. PR/fork/older-SHA/failed/skipped
or incomplete runs cannot satisfy the gate. A moved `main` blocks publication.

The writer checks out the same SHA and rechecks all gates. It creates a missing tag
at that exact commit, re-reads the tag, and creates a non-draft, non-prerelease GitHub
Release with `--verify-tag`. Existing tags are never moved and published releases are
not edited. A tag without a Release is reusable only at the same tested SHA. HTTP
403, 429 and service failures cannot be mistaken for a missing tag or release.

Only GitHub Actions' configured token is used. There is no credential extraction,
review simulation, deployment or package-index publication. Publication is not
triggered by PR code, and the privileged job does not run until the read-only gate
allows it. Concurrent completion events share a publication concurrency group.

## Release evidence and non-claims

The immutable tag is the exact commit identity, even when `main` later advances.
Release notes describe the stable surface and repeat the production-performance,
production-readiness, compliance, certification and autonomous-containment non-claims.
Synthetic metrics are not evidence about a real institution.

The release contract does not claim live branch protection, GitHub ruleset enforcement
or external security review. Those facts require separate evidence. Later versions
require a new explicit owner decision and policy update; an ordinary source change
does not authorize publication of another version.
