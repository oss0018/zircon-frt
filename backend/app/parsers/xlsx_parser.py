from app.parsers.base import BaseParser


class XlsxParser(BaseParser):
    """Extract text from XLSX files using openpyxl."""

    def parse(self, filepath: str) -> str:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            parts: list[str] = []
            for sheet in wb.worksheets:
                parts.append(f"Sheet: {sheet.title}")
                for row in sheet.iter_rows(values_only=True):
                    row_str = "\t".join(str(v) for v in row if v is not None)
                    if row_str.strip():
                        parts.append(row_str)
            wb.close()
            return "\n".join(parts)
        except Exception:
            # Fallback to pandas
            try:
                import pandas as pd
                xls = pd.ExcelFile(filepath)
                parts = []
                for sheet_name in xls.sheet_names:
                    df = xls.parse(sheet_name, dtype=str)
                    parts.append(f"Sheet: {sheet_name}")
                    parts.append(df.to_string(index=False))
                return "\n".join(parts)
            except Exception:
                return ""
