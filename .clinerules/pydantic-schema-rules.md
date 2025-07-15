## Brief overview
This rule codifies the project's architectural decision to strictly adhere to the Pydantic model compliance required by the OpenAI Agents SDK. This is a global rule for all agent and tool development to ensure system reliability.

## Pydantic Model Design
- **Strict Compliance is Mandatory:** All Pydantic models used for agent `output_type` or `FunctionTool` parameters MUST generate a "Strict JSON Schema". The `output_schema_strict=False` flag is considered an anti-pattern.
- **No Generic Dictionaries:** Avoid using `dict` or `Dict`. Always define a specific, nested `pydantic.BaseModel` for object structures to ensure the schema includes `"additionalProperties": false`.
- **Correct Optionality:** Use `typing.Optional[T]` for any field that is not guaranteed to be present. Do not rely on default `None` values for optionality.
- **No Unsupported Validators:** Business logic validation (e.g., string length, number ranges) must be performed in application code, not with `Field` constraints like `pattern`, `min_length`, or `ge`.

## Development Workflow
- **Proactive Validation:** Before integrating a new model, developers must proactively generate and inspect its JSON schema to ensure it complies with the strict rules. Use Pydantic's `TypeAdapter` for this purpose.
- **Reference Document:** For a deep dive into the rationale and specific implementation patterns, refer to the project's internal `memory-bank/pydantic_strict_schema_rule.md` document.
