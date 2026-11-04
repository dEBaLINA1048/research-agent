"""Reference management: APA strings and BibTeX export."""
import re


def _last_first(name):
    parts = name.split()
    if len(parts) < 2:
        return name
    initials = " ".join(f"{p[0]}." for p in parts[:-1])
    return f"{parts[-1]}, {initials}"


def apa(p):
    authors = p["authors"] or ["Unknown"]
    names = [_last_first(a) for a in authors[:6]]
    auth = ", ".join(names[:-1]) + (", & " if len(names) > 1 else "") + names[-1]
    if len(authors) > 6:
        auth += ", et al."
    venue = f" *{p['venue']}*." if p.get("venue") else ""
    return f"{auth} ({p['year'] or 'n.d.'}). {p['title']}.{venue} {p['url']}"


def bibtex(p, idx):
    first = (p["authors"][0].split()[-1] if p["authors"] else "anon")
    key = re.sub(r"[^A-Za-z]", "", first) + str(p["year"]) + str(idx)
    authors = " and ".join(p["authors"]) or "Unknown"
    return (
        f"@article{{{key},\n  title={{{p['title']}}},\n  author={{{authors}}},\n"
        f"  year={{{p['year']}}},\n  journal={{{p.get('venue','')}}},\n"
        f"  url={{{p['url']}}}\n}}"
    )


def all_apa(papers):
    return "\n\n".join(f"[{i+1}] {apa(p)}" for i, p in enumerate(papers))


def all_bibtex(papers):
    return "\n\n".join(bibtex(p, i + 1) for i, p in enumerate(papers))
