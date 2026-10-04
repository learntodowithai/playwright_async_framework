"""Data-provider helpers for loading static test data from Excel, CSV and JSON.

Each provider exposes a :func:`read_rows` that returns a ``list[dict]`` where
every element is a row keyed by its column / field name. A unified
:func:`read_test_data` facade dispatches on the file extension.
"""
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

import openpyxl


class ExcelDataProvider:
    """Read rows from an ``.xlsx`` worksheet (first row = headers)."""

    @staticmethod
    def read_rows(file_path: str, sheet_name: str | None = None) -> List[Dict]:
        workbook = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
        sheet = workbook[sheet_name] if sheet_name else workbook.active
        rows: Iterable[Iterable] = sheet.iter_rows(values_only=True)
        try:
            header_row = next(rows)
        except StopIteration:
            return []
        headers = [str(h).strip() for h in header_row]
        result: List[Dict] = []
        for values in rows:
            if all(v is None or v == "" for v in values):
                continue
            result.append({headers[i]: values[i] for i in range(len(headers))})
        workbook.close()
        return result


class CsvDataProvider:
    """Read rows from a ``.csv`` file using the first line as headers."""

    @staticmethod
    def read_rows(file_path: str) -> List[Dict]:
        with open(file_path, encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return [row for row in reader if any((value or "").strip() for value in row.values())]


class JsonDataProvider:
    """Read rows from a ``.json`` file.

    Supports either a top-level list of objects or a wrapper object whose
    first list-of-objects value is treated as the rows (e.g. ``{"users": [...]}``).
    """

    @staticmethod
    def read_rows(file_path: str) -> List[Dict]:
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    return value
            return [data]
        raise TypeError(f"Unsupported JSON structure in {file_path}")


def read_test_data(file_path: str) -> List[Dict]:
    """Load rows from a data file, dispatching on its extension."""
    extension = Path(file_path).suffix.lower()
    providers = {
        ".xlsx": ExcelDataProvider.read_rows,
        ".xls": ExcelDataProvider.read_rows,
        ".csv": CsvDataProvider.read_rows,
        ".json": JsonDataProvider.read_rows,
    }
    reader = providers.get(extension)
    if reader is None:
        raise ValueError(f"Unsupported data file extension: {extension}")
    return reader(file_path)


def rows_as_parametrize(rows: Iterable[Dict], id_key: str | None = None) -> tuple:
    """Return ``(params, ids)`` suitable for a single-argument parametrize.

    Each row is returned as a plain dict (no wrapping tuple) so that
    ``@pytest.mark.parametrize("row", params, ids=ids)`` passes the row dict
    straight through as the test argument.
    """
    rows = list(rows)
    ids = [str(row.get(id_key) if id_key else idx) for idx, row in enumerate(rows)]
    return [dict(row) for row in rows], ids