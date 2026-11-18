# SQL / SPARQL Demonstration and Performance

Open **[query_performance.ipynb](query_performance.ipynb)** in Jupyter or VS Code,
select a Python 3 kernel, and choose **Run All**. All execution code and SQL/SPARQL query definitions are in the
notebook cells; the notebook does not load external query files.

Start the project's services from the repository root:

```powershell
docker compose up --build --wait
```

The notebook uses the Python standard library and IPython for SPARQL.
SQL comparison requires `psycopg2`, which the project already uses. If necessary,
install it in a kernel cell with `%pip install psycopg2-binary`.
Set `COMPARE_SQL = False` in the configuration to measure SPARQL only.

## Contents

- `query_performance.ipynb`: inline SQL/SPARQL queries, repeated measurements, independent validation
  against the CSVs, and result tables with saved outputs.

Measurements and examples are displayed directly in the notebook.

## Tom Holland → Brad Pitt paths

One intermediary, with two possible final films in the catalog:

**Tom Holland → Avengers: Infinity War → Don Cheadle → Ocean's Twelve / Ocean's Thirteen → Brad Pitt.**

Three intermediaries and four distinct films:

**Tom Holland → The Impossible → Ewan McGregor → August: Osage County →
Abigail Breslin → No Reservations → Catherine Zeta-Jones → Ocean's Twelve → Brad Pitt.**

The notebook retrieves the second path from Fuseki using `VALUES`, then validates
every cast membership against the CSVs. This targeted query is separate from the benchmark.
The three-intermediary path is not the shortest: Don Cheadle already provides a shorter connection.

## Method and limitations

Each case has a first measured execution, followed by five repetitions per engine
(`REPEATS`). Queries run sequentially, alternating the engines' order.
Connections are established before timing; transfer and decoding are included.
Caches are not cleared. PostgreSQL is queried in read-only mode.

Queries use the same constraints and `LIMIT 20` without `ORDER BY`: the engines may
return different subsets of valid paths. Results are checked against the source data
outside the timed section. The measurements do not cover exhaustive path enumeration.

The three-intermediary SQL keeps the CTE from the initial comparison. Different SQL
plans, indexes, or configurations can change performance. These figures do not
demonstrate that SPARQL is generally faster. The queries traverse actor–film links,
without precomputed `knows` links or OWL reasoning.

Edit the query cells in the notebook to change execution. The notebook runs without
an external query folder.

Configuration accepts `SPARQL_ENDPOINT` and the PostgreSQL variables `PGHOST`,
`PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD`. Defaults match the local Compose services.
