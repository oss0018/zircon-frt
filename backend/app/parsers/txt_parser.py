from app.parsers.base import BaseParser


class TxtParser(BaseParser):
    def parse(self, filepath: str) -> str:
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            return ""
