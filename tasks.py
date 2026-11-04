"""Research tasks, each powered by IBM Granite."""
from .llm import GraniteLLM
from .search import search_all
from .citations import all_apa

SYS = "You are a rigorous academic research assistant. Be accurate, concise, and never invent facts or citations."


def plan_queries(llm: GraniteLLM, question: str):
    data = llm.ask_json(
        SYS,
        f'Research question: "{question}"\nReturn a JSON list of 3 short, distinct academic search queries (keywords only).',
        200,
    )
    if isinstance(data, list) and data:
        return [str(q) for q in data][:3]
    return [question]


def summarize_paper(llm: GraniteLLM, paper):
    data = llm.ask_json(
        SYS,
        f"Title: {paper['title']}\nAbstract: {paper['abstract'][:2500]}\n\n"
        'Return JSON with keys: "objective", "method", "key_findings", "limitations", "datasets_or_metrics". '
        "Use only information from the abstract; write 'Not stated' when absent.",
        500,
    )
    return data or {"objective": paper["abstract"][:300], "method": "Not stated",
                    "key_findings": "Not stated", "limitations": "Not stated",
                    "datasets_or_metrics": "Not stated"}


def _context(papers, summaries):
    lines = []
    for i, (p, s) in enumerate(zip(papers, summaries), 1):
        lines.append(
            f"[{i}] {p['title']} ({p['year']}) - Objective: {s.get('objective')} | "
            f"Method: {s.get('method')} | Findings: {s.get('key_findings')} | "
            f"Limitations: {s.get('limitations')}"
        )
    return "\n".join(lines)


def literature_review(llm, question, papers, summaries):
    return llm.ask(
        SYS,
        f"Research question: {question}\n\nSources:\n{_context(papers, summaries)}\n\n"
        "Write a literature review (4-6 paragraphs) with sections: Background, Current Approaches, "
        "Key Findings, Gaps & Limitations. Cite sources inline as [n] using ONLY the numbers above.",
        1400,
    )


def hypotheses(llm, question, papers, summaries):
    return llm.ask(
        SYS,
        f"Research question: {question}\n\nSources:\n{_context(papers, summaries)}\n\n"
        "Suggest 4 novel, testable research hypotheses grounded in the gaps above. For each give: "
        "Hypothesis, Rationale (cite [n]), and a Suggested experiment/validation.",
        1000, 0.5,
    )


def draft_paper_sections(llm, question, review, hyps):
    return llm.ask(
        SYS,
        f"Topic: {question}\n\nLiterature review:\n{review}\n\nHypotheses:\n{hyps}\n\n"
        "Draft the Abstract, Introduction, and Proposed Methodology sections of a research paper in "
        "formal academic style. Keep the [n] citations. Do not fabricate results.",
        1400, 0.4,
    )


def run_pipeline(question, per_query=4, sources=("arXiv", "OpenAlex"), max_papers=8, progress=print):
    llm = GraniteLLM()
    progress("Planning search queries with Granite...")
    queries = plan_queries(llm, question)
    progress(f"Searching literature: {queries}")
    papers = search_all(queries, per_query, sources)[:max_papers]
    if not papers:
        raise RuntimeError("No papers found. Try a broader question.")
    summaries = []
    for i, p in enumerate(papers, 1):
        progress(f"Summarizing paper {i}/{len(papers)}...")
        summaries.append(summarize_paper(llm, p))
    progress("Writing literature review...")
    review = literature_review(llm, question, papers, summaries)
    progress("Generating hypotheses...")
    hyps = hypotheses(llm, question, papers, summaries)
    progress("Drafting paper sections...")
    draft = draft_paper_sections(llm, question, review, hyps)
    return {
        "question": question, "queries": queries, "papers": papers, "summaries": summaries,
        "review": review, "hypotheses": hyps, "draft": draft,
    }


def to_markdown(r):
    md = [f"# Research Report: {r['question']}\n",
          "## Literature Review\n", r["review"], "\n## Suggested Hypotheses\n", r["hypotheses"],
          "\n## Draft Paper Sections\n", r["draft"], "\n## Paper Summaries\n"]
    for i, (p, s) in enumerate(zip(r["papers"], r["summaries"]), 1):
        md.append(f"**[{i}] {p['title']}** ({p['year']})\n")
        for k, v in s.items():
            md.append(f"- *{k.replace('_',' ').title()}*: {v}")
        md.append("")
    md += ["\n## References\n", all_apa(r["papers"])]
    return "\n".join(md)
