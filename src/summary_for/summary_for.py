def summary_for(config: dict) -> str:
    """Return the role of the sheet_todo column.

    Inputs:
        config: board config dict with `columns`, each column a
            dict with a `role`.

    Outputs:
        The `role` string for the column named `sheet_todo`.

    Side effects:
        None. Pure. Raises ValueError when there is no
        `sheet_todo` column or its role is missing, empty,
        or `none`.
    """
    columns = config.get("columns") if isinstance(config, dict) else None
    if not isinstance(columns, dict):
        raise ValueError("missing sheet_todo column")
    column = columns.get("sheet_todo")
    if not isinstance(column, dict):
        raise ValueError("missing sheet_todo column")
    role = column.get("role")
    if not isinstance(role, str) or not role or role == "none":
        raise ValueError("missing sheet_todo role")
    return role
