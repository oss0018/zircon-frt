from pathlib import Path

from app.parsers.base import BaseParser
from app.parsers.txt_parser import TxtParser
from app.parsers.csv_parser import CsvParser
from app.parsers.json_parser import JsonParser
from app.parsers.sql_parser import SqlParser

_PARSERS: dict[str, type[BaseParser]] = {
    ".txt": TxtParser,
    ".log": TxtParser,
    ".md": TxtParser,
    ".csv": CsvParser,
    ".json": JsonParser,
    ".sql": SqlParser,
}


def get_parser(filepath: str) -> BaseParser | None:
    ext = Path(filepath).suffix.lower()
    parser_cls = _PARSERS.get(ext)
    return parser_cls() if parser_cls else None
