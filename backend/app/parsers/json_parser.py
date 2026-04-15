import json

from app.parsers.base import BaseParser


class JsonParser(BaseParser):
    def parse(self, filepath: str) -> str:
        try:
            with open(filepath, encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            return ""
