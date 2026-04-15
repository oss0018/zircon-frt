"""Brand protection service — typosquatting detection + similarity scoring."""
from __future__ import annotations

import itertools
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def extract_domain(url: str) -> str:
    """Extract the base domain from a URL."""
    if "://" not in url:
        url = "https://" + url
    return urlparse(url).hostname or url


def levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein edit distance."""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def domain_similarity(original: str, candidate: str) -> float:
    """Return similarity score 0-100 based on Levenshtein distance."""
    orig = original.lower().split(".")[0]
    cand = candidate.lower().split(".")[0]
    max_len = max(len(orig), len(cand), 1)
    dist = levenshtein(orig, cand)
    return round(max(0.0, (1 - dist / max_len) * 100), 1)


def generate_typosquats(domain: str) -> list[str]:
    """Generate common typosquatting variations of a domain."""
    name = domain.split(".")[0]
    tld = ".".join(domain.split(".")[1:]) if "." in domain else "com"
    variants: set[str] = set()

    # Character omission
    for i in range(len(name)):
        variants.add(name[:i] + name[i + 1 :] + "." + tld)

    # Character transposition
    for i in range(len(name) - 1):
        t = list(name)
        t[i], t[i + 1] = t[i + 1], t[i]
        variants.add("".join(t) + "." + tld)

    # Character substitution (keyboard proximity)
    keyboard_adj: dict[str, str] = {
        "a": "sq", "b": "vn", "c": "xv", "d": "sf", "e": "wr",
        "f": "dg", "g": "fh", "h": "gj", "i": "uo", "j": "hk",
        "k": "jl", "l": "k", "m": "n", "n": "bm", "o": "ip",
        "p": "ol", "q": "wa", "r": "et", "s": "ad", "t": "ry",
        "u": "yi", "v": "cb", "w": "qe", "x": "zc", "y": "tu",
        "z": "x",
    }
    for i, ch in enumerate(name):
        for repl in keyboard_adj.get(ch, ""):
            variants.add(name[:i] + repl + name[i + 1 :] + "." + tld)

    # Common TLD variations
    for alt_tld in ["com", "net", "org", "io", "co", "info"]:
        if alt_tld != tld:
            variants.add(name + "." + alt_tld)

    # Prepend/append www
    variants.add("www-" + domain)
    variants.add(name + "-" + tld.replace(".", "") + "." + tld)

    # Remove the original
    variants.discard(domain)
    return sorted(variants)


def calculate_similarity(
    original_domain: str,
    candidate: str,
    is_in_threat_db: bool = False,
) -> float:
    """Compute composite similarity score 0-100."""
    score = domain_similarity(original_domain, candidate)
    if is_in_threat_db:
        score = min(100.0, score + 15.0)
    return score


async def run_brand_scan(
    original_url: str,
    keywords: list[str],
    threshold: float = 70.0,
) -> list[dict]:
    """
    Run a brand scan using typosquat generation + basic scoring.
    In production this would call SecurityTrails, Censys, VirusTotal etc.
    Returns list of findings with similarity scores above threshold.
    """
    domain = extract_domain(original_url)
    typosquats = generate_typosquats(domain)
    findings = []

    for candidate in typosquats:
        score = calculate_similarity(domain, candidate)
        if score >= threshold:
            findings.append(
                {
                    "found_domain": candidate,
                    "similarity_score": score,
                    "detection_sources": ["typosquat_generation"],
                    "screenshot_url": None,
                }
            )

    logger.info(
        "Brand scan for %s: %d typosquats, %d above threshold %.0f%%",
        domain,
        len(typosquats),
        len(findings),
        threshold,
    )
    return findings
