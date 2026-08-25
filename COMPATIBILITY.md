# Compatibility Policy

## Stable v1 reference surface

Version 1.0.0 defines a stable research-package contract for explainable alert-risk
evaluation on the normalized synthetic telemetry described by this repository. The
stable surface consists of:

- the names exported through `ai_threat_detection.__all__`;
- the `ai-threat-eval` and `ai-threat-generate` command names and their documented
  intent;
- the required normalized input fields in `schemas/alert-input.schema.json`;
- the exact v1 output schemas under `schemas/*.schema.json`;
- the package version exposed by `ai_threat_detection.__version__`.

The fingerprints for that surface are committed in
`release/release-contract.json` and verified by `tools/release_contract.py`.

## Semantic versioning

Removing or renaming an exported symbol, removing a CLI command, changing required
input semantics incompatibly, or making a public v1 schema reject a previously valid
v1 document requires a future major version. Backward-compatible additions belong in
a minor version. Compatible fixes belong in a patch version.

Exact numeric model output is reproducible only within a recorded runtime and
dependency environment. Evaluation reports therefore record Python, NumPy, pandas and
scikit-learn versions. A compatible dependency update may change floating-point model
results without changing the stable data or API contract; such a change must still be
documented and re-evaluated.

## Research and governance boundary

Stable package/API status is not a claim of real-world detection accuracy, production
fitness, regulatory compliance, certification or authority to automate containment.
Synthetic labels and example thresholds remain outside the stable performance
contract. Operational adopters must perform their own validation, approval, monitoring
and rollback design.

## Release decisions

Merging a source-level stable reference does not create a Git tag, GitHub Release,
package publication, container publication or deployment. Each publication remains an
explicit human decision against one reviewed, green commit.
