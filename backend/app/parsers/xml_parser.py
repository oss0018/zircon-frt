import xml.etree.ElementTree as ET
from app.parsers.base import BaseParser


class XmlParser(BaseParser):
    """Extract text from XML files using xml.etree with lxml fallback."""

    def parse(self, filepath: str) -> str:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            return " ".join(root.itertext())
        except ET.ParseError:
            pass
        except Exception:
            pass

        # Fallback: lxml
        try:
            from lxml import etree  # type: ignore[import]
            with open(filepath, "rb") as f:
                tree = etree.parse(f)
            return " ".join(tree.getroot().itertext())
        except Exception:
            return ""
