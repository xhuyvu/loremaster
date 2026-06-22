"""One-time build script: crawl output → srd_data.json."""
import json
import re
from pathlib import Path

CRAWL_FILE = Path(__file__).parent / "scraped" / "crawl-output.json"
OUTPUT_FILE = Path(__file__).parent / "srd_data.json"

TYPE_MAP = {
    "spell-descriptions": "spell",
    "creature-stat-blocks": "monster",
    "rules-glossary": "glossary",
    "feats": "feat",
    "equipment": "equipment",
    "character-classes": "class",
    "character-origins": "origin",
    "magic-items-a-z": "magic-item",
    "magic-items": "magic-item",
    "playing-the-game": "rule",
    "creating-a-character": "rule",
    "the-basics": "rule",
    "dms-toolbox": "rule",
    "spells": "rule",
    "how-to-use-a-monster": "rule",
    "tracking-sheets": "other",
    "credits": "other",
}

HEADING3_BASED = {
    "spell-descriptions", "creature-stat-blocks", "rules-glossary",
    "feats", "equipment", "magic-items-a-z", "magic-items",
}

SKIP_H3 = {
    "Spells (A)", "Spells (B)", "Spells (C)", "Spells (D)", "Spells (E)",
    "Spells (F)", "Spells (G)", "Spells (H)", "Spells (I)", "Spells (J)",
    "Spells (K)", "Spells (L)", "Spells (M)", "Spells (N)", "Spells (O)",
    "Spells (P)", "Spells (R)", "Spells (S)", "Spells (T)", "Spells (U)",
    "Spells (V)", "Spells (W)", "Spells (X)", "Spells (Z)",
    "Glossary Conventions", "Rules Definitions",
    "Magic Item Categories", "Magic Item Rarity", "Awarding Magic Items",
    "Activating a Magic Item", '"The Next Dawn"', "Cursed Items",
    "Magic Item Resilience", "Crafting Magic Items", "Sentient Magic Items",
}

SKIP_H2 = {
    "Back to Top", "Jump to",
}


def get_type(url: str) -> str:
    for seg, t in TYPE_MAP.items():
        if seg in url:
            return t
    return "other"


def clean_heading(text: str) -> str:
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = text.strip().strip("#").strip()
    return text


def make_key(etype: str, name: str) -> str:
    key = f"{etype}_{name}".lower()
    key = key.replace("'", "").replace("'", "").replace("-", "_")
    key = key.replace(" ", "_").replace("/", "_").replace("&", "and")
    key = re.sub(r'[^a-z0-9_]', '', key)
    key = re.sub(r'_+', '_', key).strip("_")
    return key


def split_sections(lines: list, split_h3: bool, skip_set: set) -> list:
    sections = []
    start = None
    current_name = None
    for i, line in enumerate(lines):
        is_h2 = line.startswith("## ") and not line.startswith("### ")
        is_h3 = line.startswith("### ")
        if is_h2 and not split_h3:
            name = clean_heading(line[3:])
            if name and name not in skip_set:
                if start is not None:
                    sections.append((current_name, start, i))
                start = i
                current_name = name
        elif is_h3 and split_h3:
            name = clean_heading(line[4:])
            if name and name not in skip_set:
                if start is not None:
                    sections.append((current_name, start, i))
                start = i
                current_name = name
    if start is not None:
        sections.append((current_name, start, len(lines)))
    return sections


def build():
    raw = json.loads(CRAWL_FILE.read_text())
    pages = raw["data"] if "data" in raw else raw

    data = {}
    for page in pages:
        url = page.get("metadata", {}).get("url", "")
        md = page.get("markdown", "") or ""
        lines = md.split("\n")

        etype = get_type(url)
        path = url.rstrip("/").split("/")[-1]
        split_h3 = path in HEADING3_BASED
        skip = SKIP_H3 if split_h3 else SKIP_H2

        sections = split_sections(lines, split_h3, skip)

        for name, s, e in sections:
            content = "\n".join(lines[s:e]).strip()
            if not content:
                continue
            key = make_key(etype, name)
            existing = data.get(key)
            if existing:
                existing["content"] += "\n\n" + content
            else:
                data[key] = {"type": etype, "name": name, "content": content}

    OUTPUT_FILE.write_text(json.dumps(data, indent=2))
    print(f"OK — {len(data)} entries → {OUTPUT_FILE}")

    # quick stats
    by_type = {}
    for v in data.values():
        by_type.setdefault(v["type"], 0)
        by_type[v["type"]] += 1
    for t, c in sorted(by_type.items()):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    build()
