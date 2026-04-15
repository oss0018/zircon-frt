from app.parsers.base import BaseParser


class SqlParser(BaseParser):
    def parse(self, filepath: str) -> str:
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                content = f.read()
            # Return raw SQL content (good enough for text indexing)
            return content
        except Exception:
            return ""
