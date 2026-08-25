# Contributing

Contributions that improve validation, evaluation quality, explainability, tests or
documentation are welcome.

## Development setup

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
ruff check .
pytest
~~~

## Pull requests

- Keep changes focused and explain the security or evaluation impact.
- Add or update tests for behavioural changes.
- Update public schemas and compatibility notes for contract changes.
- Run `python tools/release_contract.py --emit --verify`; an intentional API, schema or
  reference-dataset change must update the pinned release contract in the same pull
  request and follow the versioning policy.
- Do not commit real telemetry, credentials, internal architecture or customer data.
- Distinguish measured results from assumptions and proposed future work.
- Preserve deterministic behaviour unless a change explicitly documents why it cannot.

By contributing, you agree that your contribution is licensed under the MIT License.
