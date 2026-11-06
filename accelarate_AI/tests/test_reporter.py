import pandas as pd
import pytest

from agents import reporter


@pytest.fixture
def gold_parquet(tmp_path):
    path = tmp_path / "fact_orders.parquet"
    pd.DataFrame({"category": ["A", "B"], "total_amount": [100, 200]}).to_parquet(
        path, index=False
    )
    return str(path)


def test_load_gold_tables_registers_table(gold_parquet):
    con = reporter.load_gold_tables([gold_parquet])

    rows = reporter.execute_query(con, "SELECT * FROM fact_orders ORDER BY category")

    assert rows == [
        {"category": "A", "total_amount": 100},
        {"category": "B", "total_amount": 200},
    ]


def test_execute_query_runs_aggregation(gold_parquet):
    con = reporter.load_gold_tables([gold_parquet])

    rows = reporter.execute_query(
        con, "SELECT SUM(total_amount) AS total FROM fact_orders"
    )

    assert rows == [{"total": 300}]


def test_write_report_creates_html_file(tmp_path, monkeypatch):
    monkeypatch.setattr(reporter, "REPORTS_DIR", tmp_path)

    out_path = reporter.write_report(
        run_id="abcdef12-3456", direct_answer="Category B leads", rows=[{"category": "B"}]
    )

    content = open(out_path, encoding="utf-8").read()
    assert "Category B leads" in content
    assert out_path.endswith("report_abcdef12.html")