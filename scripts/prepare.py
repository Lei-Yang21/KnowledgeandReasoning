"""Initialize an empty database and publish a complete RDF export for Fuseki."""

import csv
import os
from pathlib import Path
import runpy
import subprocess

import psycopg2
from psycopg2 import sql


ROOT = Path(__file__).resolve().parents[1]
TABLE_FILES = {
    "person": "person", "country": "country", "rating": "rating", "show": "show",
    "rated": "rated", "filmed_in": "produced", "directed_by": "director",
    "acted_in": "actor", "genre": "genre", "genresof": "belong",
}


def expected_counts():
    counts = {}
    for table, filename in TABLE_FILES.items():
        with (ROOT / "submit/Database" / f"{filename}.csv").open(encoding="utf-8", newline="") as stream:
            counts[table] = sum(1 for _ in csv.DictReader(stream))
    return counts


def database_counts():
    with psycopg2.connect(connect_timeout=10) as connection:
        with connection.cursor() as cursor:
            counts = {}
            for table in TABLE_FILES:
                cursor.execute("SELECT to_regclass(%s)", (table,))
                if cursor.fetchone()[0] is None:
                    counts[table] = 0
                else:
                    cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
                    counts[table] = cursor.fetchone()[0]
    return counts


def main():
    expected = expected_counts()
    actual = database_counts()
    if not any(actual.values()):
        print("Importing CSV files into the empty database...", flush=True)
        runpy.run_path(str(ROOT / "submit/Database/Main.py"), run_name="__main__")
        actual = database_counts()
    if actual != expected:
        raise RuntimeError(
            f"Database contents differ from the CSV counts; no existing data was replaced. "
            f"Expected: {expected}; actual: {actual}"
        )
    print(f"Database verified (existing rows preserved): {actual}", flush=True)

    # Publish only after a successful conversion, keeping the previous RDF on failure.
    pending = Path("/data/output.pending.ttl")
    config = Path("/tmp/r2rml.properties")
    config.write_text(
        f"connectionURL=jdbc:postgresql://{os.environ['PGHOST']}:5432/{os.environ['PGDATABASE']}\n"
        f"user={os.environ['PGUSER']}\npassword={os.environ['PGPASSWORD']}\n"
        f"mappingFile={ROOT / 'submit/mapping.ttl'}\noutputFile={pending}\nformat=TURTLE\n",
        encoding="utf-8",
    )
    subprocess.run(["java", "-Xmx2g", "-jar", str(ROOT / "r2rml.jar"), str(config)], check=True, cwd=ROOT)
    if not pending.exists() or pending.stat().st_size == 0:
        raise RuntimeError("R2RML did not generate a nonempty RDF export")
    pending.replace("/data/output.ttl")
    print("RDF export ready; Fuseki can start.", flush=True)


if __name__ == "__main__":
    main()
