# Data Quality Library

A reusable Teradata validation framework I designed and built — generic and
relational checks, severity folding, and HTML reporting. Now the standard across the team's.

## Why

Before: ad-hoc checks scattered across scripts, inconsistent output, no
severity model, no unified reporting.

After: one `check()` contract, composable check functions, a severity model,
and a single report format — the same checks used everywhere, returning the
same shape.

## Design

- **Unified result contract** — every check returns the same dict:
  `check_name`, `table_name`, `columns`, `status`, `rows_found`, `truncated`,
  `data`, `sql`, `error`.
- **Pass/fail rule** — empty result → `PASS`; non-empty → the check's severity;
  exception → `ERROR`.
- **Severity model** — `PASS` / `WARNING` / `ERROR` / `CRITICAL`, folded to one
  overall status by max weight (`get_overall_status`).
- **`limit` truncates `data`, never `rows_found`** — you always see the full
  violation count, even when sample rows are capped.
- **Isolated connections** — each check opens and closes its own connection, so
  one failure doesn't cascade.

## Check catalog

| Function | dbt equivalent | Validates |
|---|---|---|
| `check_duplicates` | `unique` | No duplicate combinations of columns |
| `check_nulls` | `not_null` | No NULLs in specified columns |
| `check_range` | (custom) | Values within `[min, max]` |
| `check_accepted_values` | `accepted_values` | Column values in an allowed set |
| `check_relationships` | `relationships` | Referential integrity (orphan detection) |

## Reporting

`run_checks()` aggregates results into an overall status, pass/fail counts,
and a per-severity breakdown. `render_warnings_html()` renders the failed
checks as an HTML table for embedding in reports or emails.

The severity model lets a pipeline fail on `CRITICAL` while only warning
on `WARNING`.

## Usage

See [`examples/`](./examples/) for real (sanitized) cases.

```python
from data_quality import check_relationships, run_checks

results = [
    check_relationships(
        source_table="fct_orders",
        source_column="customer_id",
        target_table="dim_customers",
        target_column="customer_id",
        severity=CRITICAL,
    ),
    check_duplicates(
        table_name="fct_orders",
        unique_columns=["order_id"],
        severity=CRITICAL,
    ),
]

summary = run_checks(results)
# {"overall_status": "PASS", "total": 2, "passed": 2, "failed": 0, ...}