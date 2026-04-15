import pandas as pd

from app.parsers.base import BaseParser


class CsvParser(BaseParser):
    def parse(self, filepath: str) -> str:
        try:
            df = pd.read_csv(filepath, dtype=str, nrows=10000)
            return df.to_string(index=False)
        except Exception:
            return ""
