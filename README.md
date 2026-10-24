# analytics-engineering-portfolio

Real-world case studies in SQL optimization, data modeling, and analytics
engineering — drawn from hands-on experience with Teradata, Python, Airflow,
and dbt.

## Projects

### [dbt] Re-registrations Modeling
*(coming soon — placeholder)*

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