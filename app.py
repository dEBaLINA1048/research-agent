import os
import re

import streamlit as st

from agent.tasks import run_pipeline, to_markdown
from agent.citations import all_apa, all_bibtex

st.set_page_config(page_title="Research Agent (IBM Granite)", page_icon="🔬", layout="wide")
st.title("🔬 Research Agent")
st.caption("Powered by IBM Granite on watsonx.ai · IBM Cloud Lite")

with st.sidebar:
    st.header("Settings")
    sources = st.multiselect("Sources", ["arXiv", "OpenAlex"], default=["arXiv", "OpenAlex"])
    per_query = st.slider("Papers per query per source", 2, 8, 4)
    max_papers = st.slider("Max papers analysed", 3, 15, 8)
    st.info("Model: " + os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-8b-instruct"))

question = st.text_area("Research question",
                        placeholder="e.g. How effective are transformer models for early detection of diabetic retinopathy?",
                        height=100)

if st.button("Run research", type="primary", disabled=not question.strip()):
    status = st.status("Working...", expanded=True)
    try:
        result = run_pipeline(question.strip(), per_query, tuple(sources), max_papers,
                              progress=lambda m: status.write(m))
        st.session_state["result"] = result
        status.update(label="Done", state="complete")
    except Exception as ex:
        status.update(label="Failed", state="error")
        st.error(str(ex))

r = st.session_state.get("result")
if r:
    t1, t2, t3, t4, t5 = st.tabs(["Literature review", "Papers & summaries", "Hypotheses",
                                  "Paper draft", "References & export"])
    with t1:
        st.markdown(r["review"])
    with t2:
        for i, (p, s) in enumerate(zip(r["papers"], r["summaries"]), 1):
            with st.expander(f"[{i}] {p['title']} ({p['year']}) - {p['source']}"):
                st.write(", ".join(p["authors"][:6]))
                st.markdown(f"[Open paper]({p['url']})")
                for k, v in s.items():
                    st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
    with t3:
        st.markdown(r["hypotheses"])
    with t4:
        st.markdown(r["draft"])
    with t5:
        st.text(all_apa(r["papers"]))
        c1, c2 = st.columns(2)
        c1.download_button("Download report (.md)", to_markdown(r), "research_report.md")
        c2.download_button("Download references (.bib)", all_bibtex(r["papers"]), "references.bib")
        if os.getenv("COS_BUCKET") and st.button("Save to IBM Cloud Object Storage"):
            from agent.storage import save_to_cos
            slug = re.sub(r"\W+", "_", r["question"])[:40]
            st.success(save_to_cos(f"reports/{slug}.md", to_markdown(r)))
