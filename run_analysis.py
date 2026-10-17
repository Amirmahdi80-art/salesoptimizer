import os
import sys
import django

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import pymysql
from salesoptimizer.models import Sqlchunk  
from django.conf import settings


def get_chunk() -> Sqlchunk:
    obj, _ = Sqlchunk.objects.get_or_create(pk=1)
    return obj


def load_sql(path: str, chunk: Sqlchunk) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        sql = fh.read()

    replacements = {
        "@@vt@@": chunk.vt,
        "@@discount_quality@@": chunk.discount_quality,
        "@@tag@@": chunk.tag,
        "@@action@@": chunk.action,
    }
    for token, value in replacements.items():
        sql = sql.replace(token, value)

    return sql


def split_statements(sql: str) -> list[str]:
    return [s.strip() for s in sql.split(";") if s.strip()]


def run(sql_path: str = "analysis.sql") -> None:
    chunk = get_chunk()
    sql = load_sql(sql_path, chunk)
    statements = split_statements(sql)

    db = settings.DATABASES["default"]
    conn = pymysql.connect(
        host=db["HOST"],
        port=int(db.get("PORT") or 3306),
        user=db["USER"],
        password=db["PASSWORD"],
        database="salesoptimizer",
        charset="utf8mb4",
        autocommit=False,
    )

    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
        print(f"Done — {len(statements)} statement(s) executed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    sql_path = sys.argv[1] if len(sys.argv) > 1 else "analysis.sql"
    run(sql_path)
