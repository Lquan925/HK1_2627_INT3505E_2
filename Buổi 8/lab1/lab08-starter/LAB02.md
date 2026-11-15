# Lab 2: OpenAPI and Flask response contracts

The specification fixes GET /books operationId, removes content from DELETE's
204 response, and declares Book.year as integer (nullable).

Run from this directory:

```sh
spectral lint openapi.yaml --ruleset .spectral.yml --fail-severity hint
python -m pytest -v -p no:cacheprovider
```

On Windows, use `spectral.cmd` if PowerShell blocks the npm script wrapper.
Output is recorded in `reports/spectral-lint.txt` and
`reports/lab02-verification.txt`.

The custom `response-200-nonempty-schema` rule requires at least one property
on a JSON object response, or on the object items of an array response.
Spectral resolves local references before checking this rule, so Book references
are checked too. It rejects `{}`, `{type: object}`, empty `properties`, and
array items without declared fields. Arrays remain valid for GET /books.
The other custom rules reject content on 204 and a non-integer Book.year.

Spectral checks the specification, not Flask execution. The pytest contract
tests validate actual create, get, list, and update responses against the Book
schema loaded from openapi.yaml, and verify DELETE returns an empty body.
OpenAPI 3.0 `nullable` is translated to JSON Schema's null type for validation.
Required fields, field types, and additionalProperties are enforced.
Three negative tests monkeypatch Flask's serializer to return a string year,
omit title, or add an unexpected field; each must raise ValidationError.
This demonstrates how a valid specification can still catch incorrect Flask
responses when paired with contract tests.
