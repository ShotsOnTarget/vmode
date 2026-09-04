purpose: validate one column table from the TOML config and list its problems
signature: column_valid(name: str, column: dict) -> list[str]
inputs: name: the column name, used only in messages. column: one column table from the TOML as a dict.
outputs: list of problems as 'field: reason' strings, empty when valid
side effects: none
work item id: 0003-2-column_valid-code
