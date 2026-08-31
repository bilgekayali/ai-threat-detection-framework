import copy
import json

import pytest

from tools import release_contract


@pytest.fixture
def manifest():
    return json.loads(release_contract.MANIFEST_PATH.read_text(encoding="utf-8"))


def test_explicit_github_only_publication_decision(manifest):
    release_contract._verify_publication_decision(manifest)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("requires_human_release_decision", False),
        ("github_release_authorized", False),
        ("github_release_authorized", "true"),
        ("source_promotion_only", True),
        ("package_publication_authorized", True),
        ("container_publication_authorized", True),
        ("deployment_authorized", True),
        ("independent_review_completed", True),
    ],
)
def test_approval_cannot_be_missing_or_expanded(manifest, field, value):
    manifest[field] = value
    with pytest.raises(SystemExit):
        release_contract._verify_publication_decision(manifest)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authorized", False),
        ("repository", "other/repository"),
        ("release_version", "1.0.1"),
        ("required_workflows", {".github/workflows/ci.yml": "CI"}),
    ],
)
def test_publication_policy_must_match_the_release(manifest, monkeypatch, field, value):
    policy = json.loads(
        (release_contract.ROOT / "release" / "publish-policy.json").read_text(encoding="utf-8")
    )
    mutated = copy.deepcopy(policy)
    mutated[field] = value
    monkeypatch.setattr(release_contract, "_load_json", lambda _path: mutated)
    with pytest.raises(SystemExit, match="publication policy"):
        release_contract._verify_publication_decision(manifest)
