"""Check relative markdown links (and #anchors) under a folder; write external URLs to a file.

Usage: python3 tools/check_links.py <folder> <urls_out.txt>
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

root = Path(sys.argv[1]).resolve()
pages = {p.resolve(): p.read_text() for p in root.rglob("*.md")}
link_re = re.compile(r"\]\(([^)\s]+)\)")
code_re = re.compile(r"`[^`\n]*`|```.*?```", re.S)


def anchors(text):
    ids = set(re.findall(r'<a id="([^"]+)"', text))
    for h in re.findall(r"^#+\s+(.*)$", text, re.M):
        slug = re.sub(r"[^\w\- ]", "", h.lower()).strip().replace(" ", "-")
        ids.add(slug)
    return ids


bad, external = [], set()
for path, text in sorted(pages.items()):
    for target in link_re.findall(code_re.sub("", text)):
        if target.startswith(("http://", "https://")):
            external.add(target)
            continue
        file, _, frag = unquote(target).partition("#")
        dest = (path.parent / file).resolve() if file else path
        rel = path.relative_to(root)
        if dest not in pages:
            bad.append(f"{rel}: missing file -> {target}")
        elif frag and frag not in anchors(pages[dest]):
            bad.append(f"{rel}: missing anchor -> {target}")

print("\n".join(bad) or f"All internal links OK ({len(pages)} pages)")
Path(sys.argv[2]).write_text("\n".join(sorted(external)))
print(f"{len(external)} unique external URLs written to {sys.argv[2]}")
