import sys
from agent.tasks import run_pipeline, to_markdown

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or input("Research question: ")
    out = to_markdown(run_pipeline(q))
    with open("research_report.md", "w", encoding="utf-8") as f:
        f.write(out)
    print("Saved research_report.md")
