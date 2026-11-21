# analytics-engineer-portfolio

Real-world case studies in SQL optimization, data modeling, and analytics
engineering — drawn from hands-on experience with Teradata, Python, Airflow,
and dbt.

## Projects

### [dbt Monetizing Dashboard Modeling](./monetizing-dashboard-dbt/)
Layered dbt project (staging → intermediate → marts) modelling a cross-sell
monetizing dashboard at daily / weekly / monthly grain. Grain-aware tests,
`COUNT(DISTINCT)` metrics, and a singular test for cross-grain consistency.
Runs locally on DuckDB — `pip install` + `dbt build`, no cloud account.

*Stack: dbt, DuckDB, SQL, data modeling, testing*

### [Campaign Aggregation Optimization](./campaign-aggregation-optimization/)

Reworked a weekly Teradata procedure producing 16 slice combinations per
campaign (a `GROUPING SETS`-style pattern implemented as 16 INSERTs). Split
the volatile table by event distribution (views ~80%, opens ~15%, clicks ~5%),
replaced `COUNT(DISTINCT CASE ...)` with `COUNT(DISTINCT)`, and restructured
each block into 1 INSERT + 2 UPDATE. Achieved ~4x reduction in CPU total time,
IO operations, and runtime.

*Stack: Teradata SQL, data modeling*

_Stack: Teradata SQL, data modeling_

### [Teradata UDF Optimization](./teradata-udf-optimization/)
Replaced 6–7 nested `SUBSTR` calls with a single `STRTOK` in a
widely-used UDF, achieving ~4x CPU reduction on 10M+ row workloads.
Benchmarked and reproducible with generated test data.

*Stack: Teradata SQL, Python, benchmarking*

### [Excel VBA Zero Row Removal](./excel-vba-deleting-zero-rows/)
Automated manual cleanup of 130+ worksheet order files, saving ~15 hours/week
across a team of 30 purchasing managers.

*Stack: Excel VBA, process automation*

## Data Quality Library

A reusable Teradata validation framework I designed and built — generic and
relational checks, severity folding, and HTML reporting. Now used across the
team's data pipelines.

[→ Read the case study](./data-quality-library/)

*Stack: Python, Teradata SQL, testing*

---

## About

These projects reflect real production work, adapted for a public
portfolio. All data and proprietary details have been anonymized.