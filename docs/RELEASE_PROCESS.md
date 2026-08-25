# Release Process

Version and publication are separate decisions.

1. Prepare release changes on a non-default branch.
2. Run lint, tests, schema validation, full-dataset evaluation and clean-wheel smoke.
3. Run `python tools/release_contract.py --emit --verify` and pin the exact API, schema
   and reference-dataset fingerprints.
4. Generate the dependency evidence with
   `python tools/build_sbom.py --output dependency-sbom.json`.
5. Open a pull request and require CI, CodeQL and Stable Release Gate success on its
   exact head SHA.
6. Review and squash-merge the approved head into `main`.
7. Verify the same workflow set succeeds on the exact `main` merge commit.
8. Make a separate human decision before creating a `v1.0.0` tag, GitHub Release,
   package publication, container publication or deployment.

The release contract records a source-level stable reference. It does not claim that
live branch protection, a GitHub ruleset, external security review, package publication
or deployment exists. Those facts require separate evidence.

## Release notes

Release notes must identify the exact target commit, describe stable interfaces and
repeat the production-performance, production-readiness, compliance, certification and
autonomous-containment non-claims. Synthetic metrics must not be presented as evidence
about a real institution.
