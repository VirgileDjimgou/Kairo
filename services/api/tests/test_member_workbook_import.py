from decimal import Decimal

from openpyxl import Workbook

from app.db.import_members_workbook import load_rows, slugify


def test_slugify_creates_ascii_member_login_component() -> None:
    assert slugify("D'Örte - N'Diaye") == "d-orte-n-diaye"


def test_load_rows_uses_total_and_accepts_missing_trailing_remark(tmp_path) -> None:
    workbook_path = tmp_path / "members.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Feuille 2"
    worksheet.append(
        [
            "Nom",
            "prenom",
            "email",
            "inscription",
            "1ere tranche",
            "2em tranche",
            "3em tranche",
            "4em tranche",
            "5em tranche",
            "6em tranche",
            "Total",
            "remarque",
        ]
    )
    worksheet.append(["Dörte", None, None, 10, 20, None, None, None, None, None, 35])
    workbook.save(workbook_path)

    rows = load_rows(workbook_path, "Feuille 2")

    assert len(rows) == 1
    assert rows[0].first_name == "Membre"
    assert rows[0].total == Decimal("35.00")
    assert rows[0].payments["inscription"] == Decimal("10.00")
    assert rows[0].login_email == "0001-dorte@demo.local"
