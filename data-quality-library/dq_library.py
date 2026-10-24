"""
Data Quality Library
====================

Reusable validation framework for Teradata.

Every check returns the same result contract:
    check_name, table_name, columns, status, rows_found,
    truncated, data, sql, error

Pass/fail rule:
    empty result  -> PASS
    non-empty     -> the check's severity
    exception     -> ERROR

Credentials are read from environment variables. In production they are
pulled from a secrets vault; this public version uses env vars to avoid
any internal dependency.
"""

import html
import os

import teradatasql


TD_HOST = os.environ["TD_HOST"]
TD_USER = os.environ["TD_USER"]
TD_PASSWORD = os.environ["TD_PASSWORD"]


PASS = "PASS"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"

SEVERITY_ORDER = {
    PASS: 0,
    WARNING: 1,
    ERROR: 2,
    CRITICAL: 3,
}


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def _get_connection():
    """Open a fresh Teradata connection for a single check."""
    return teradatasql.connect(
        host=TD_HOST,
        user=TD_USER,
        password=TD_PASSWORD,
    )


# ---------------------------------------------------------------------------
# Base contract
# ---------------------------------------------------------------------------

def check(
    check_name: str,
    table_name: str,
    query: str,
    severity: str = WARNING,
    columns: list[str] | None = None,
    limit: int | None = 100,
) -> dict:
    """
    Base check: runs SQL in its own connection and returns the result contract.

    - empty result  -> PASS
    - non-empty     -> severity (WARNING / ERROR / CRITICAL)
    - exception     -> ERROR

    data        -- list of dicts (result rows)
    rows_found  -- full count of violating rows
    limit       -- truncates data, never rows_found
    """
    error = None
    data = None
    rows_found = None
    truncated = False

    try:
        conn = _get_connection()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                col_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
            finally:
                cursor.close()
        finally:
            conn.close()

        rows_found = len(rows)
        status = PASS if rows_found == 0 else severity

        if limit is not None and rows_found > limit:
            truncated = True
            rows = rows[:limit]

        data = [dict(zip(col_names, row)) for row in rows]

    except Exception as e:
        status = ERROR
        error = f"{type(e).__name__}: {e}"

    return {
        "check_name": check_name,
        "table_name": table_name,
        "columns": columns,
        "status": status,
        "rows_found": rows_found,
        "truncated": truncated,
        "data": data,
        "sql": query,
        "error": error,
    }


# ---------------------------------------------------------------------------
# Duplicates
# ---------------------------------------------------------------------------

def check_duplicates(
    table_name: str,
    unique_columns: list[str],
    filters: list[str] | None = None,
    severity: str = WARNING,
    limit: int | None = 100,
) -> dict:
    """
    Checks that the combination of `unique_columns` has no duplicates.

    Returns groups where the combination occurs more than once.
    """
    columns = ", ".join(unique_columns)

    where_clause = ""
    if filters:
        where_clause = "WHERE " + "\nAND ".join(filters)

    query = f"""
SELECT
    {columns},
    COUNT(*) AS duplicate_count
FROM {table_name}
{where_clause}
GROUP BY {columns}
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
"""

    return check(
        check_name="duplicates",
        table_name=table_name,
        columns=unique_columns,
        severity=severity,
        query=query,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Nulls
# ---------------------------------------------------------------------------

def check_nulls(
    table_name: str,
    columns: list[str],
    filters: list[str] | None = None,
    severity: str = WARNING,
    limit: int | None = 100,
) -> dict:
    """
    Checks that the given columns contain no NULLs.

    Returns rows where at least one of the columns is NULL.
    """
    null_conditions = "\nOR ".join(f"{col} IS NULL" for col in columns)

    where_clause = f"WHERE ({null_conditions})"
    if filters:
        where_clause += "\nAND " + "\nAND ".join(filters)

    query = f"""
SELECT *
FROM {table_name}
{where_clause}
"""

    return check(
        check_name="nulls",
        table_name=table_name,
        columns=columns,
        severity=severity,
        query=query,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Range
# ---------------------------------------------------------------------------

def check_range(
    table_name: str,
    column: str,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    filters: list[str] | None = None,
    severity: str = WARNING,
    limit: int | None = 100,
) -> dict:
    """
    Checks that values in `column` fall within [min_value, max_value].

    Returns rows outside the bounds. A None bound is not checked.
    At least one bound must be provided.
    """
    conditions = []
    if min_value is not None:
        conditions.append(f"{column} < {min_value}")
    if max_value is not None:
        conditions.append(f"{column} > {max_value}")

    if not conditions:
        raise ValueError("Provide at least one bound: min_value or max_value")

    where_clause = "WHERE (" + "\nOR ".join(conditions) + ")"

    if filters:
        where_clause += "\nAND " + "\nAND ".join(filters)

    query = f"""
SELECT *
FROM {table_name}
{where_clause}
"""

    return check(
        check_name="range",
        table_name=table_name,
        columns=[column],
        severity=severity,
        query=query,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Accepted values
# ---------------------------------------------------------------------------

def check_accepted_values(
    table_name: str,
    column: str,
    accepted_values: list[str] | list[int],
    filters: list[str] | None = None,
    severity: str = WARNING,
    limit: int | None = 100,
) -> dict:
    """
    Checks that `column` contains only accepted values.

    Returns rows whose value is not in `accepted_values`.
    NULL is not treated as a violation (use check_nulls for that).
    """
    values_sql = ", ".join(
        f"'{v}'" if isinstance(v, str) else str(v)
        for v in accepted_values
    )

    where_clause = f"WHERE {column} NOT IN ({values_sql})"

    if filters:
        where_clause += "\nAND " + "\nAND ".join(filters)

    query = f"""
SELECT *
FROM {table_name}
{where_clause}
"""

    return check(
        check_name="accepted_values",
        table_name=table_name,
        columns=[column],
        severity=severity,
        query=query,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Relationships
# ---------------------------------------------------------------------------

def check_relationships(
    source_table: str,
    source_column: str,
    target_table: str,
    target_column: str,
    source_filters: list[str] | None = None,
    target_filters: list[str] | None = None,
    severity: str = WARNING,
    limit: int | None = 100,
) -> dict:
    """
    Checks referential integrity: every value in source_column (source_table)
    must exist in target_column (target_table).

    Returns distinct orphan values (missing_value).
    target_filters are applied inside the JOIN ON clause (filter the target
    before the orphan check); source_filters narrow the source side.
    """
    target_join_condition = ""
    if target_filters:
        target_join_condition = "\nAND " + "\nAND ".join(target_filters)

    source_where = ""
    if source_filters:
        source_where = "AND " + "\nAND ".join(source_filters)

    query = f"""
SELECT DISTINCT
    src.{source_column} AS missing_value
FROM {source_table} src
LEFT JOIN {target_table} tgt
    ON src.{source_column} = tgt.{target_column}
{target_join_condition}
WHERE tgt.{target_column} IS NULL
  AND src.{source_column} IS NOT NULL
{source_where}
"""

    return check(
        check_name="relationships",
        table_name=source_table,
        columns=[source_column],
        severity=severity,
        query=query,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def get_overall_status(checks: list[dict]) -> str:
    """Fold per-check statuses into one overall status by max severity."""
    return max(
        (c["status"] for c in checks),
        key=SEVERITY_ORDER.get,
        default=PASS,
    )


def run_checks(checks: list[dict]) -> dict:
    """Aggregate results into an overall status and pass/fail summary."""
    overall = get_overall_status(checks)
    passed = [c for c in checks if c["status"] == PASS]
    failed = [c for c in checks if c["status"] != PASS]

    by_severity = {}
    for c in checks:
        by_severity[c["status"]] = by_severity.get(c["status"], 0) + 1

    return {
        "overall_status": overall,
        "total": len(checks),
        "passed": len(passed),
        "failed": len(failed),
        "by_severity": by_severity,
        "failed_checks": failed,
    }


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def render_warnings_html(
    checks: list[dict],
    statuses: list[str] | None = None,
) -> str:
    """
    Render the selected checks as an HTML table.

    checks   -- list of check_* results
    statuses -- which statuses to include (default: [WARNING])
                e.g. [WARNING, CRITICAL, ERROR]

    Returns an HTML string, or "" if there are no matching checks.
    """
    statuses = statuses or [WARNING]

    selected = [c for c in checks if c["status"] in statuses]
    if not selected:
        return ""

    rows = []
    for c in selected:
        rows.append(f"""
<tr>
    <td valign="top"><b>{html.escape(c['check_name'])}</b></td>
    <td valign="top">{html.escape(c['status'])}</td>
    <td valign="top">{html.escape(c['table_name'])}</td>
    <td valign="top">{html.escape(str(c['columns']))}</td>
    <td valign="top">{c['rows_found']}</td>
    <td valign="top"><pre style="white-space:pre-wrap;margin:0;font-size:11px;">{html.escape(c['sql'].strip())}</pre></td>
</tr>
""")

    return f"""
<table border="1" cellspacing="0" cellpadding="4"
style="border-collapse:collapse;font-family:Calibri;font-size:12px;">
<thead>
<tr>
    <th>check</th>
    <th>status</th>
    <th>table</th>
    <th>columns</th>
    <th>rows_found</th>
    <th>SQL</th>
</tr>
</thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
"""