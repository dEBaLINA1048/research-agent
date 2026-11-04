# Research Agent - IBM Granite + IBM Cloud Lite

An autonomous research assistant. Give it a research question and it will:

1. **Plan** search queries (IBM Granite)
2. **Search** arXiv and OpenAlex for literature
3. **Summarize** each paper into objective / method / findings / limitations / datasets
4. **Synthesize** a literature review with inline [n] citations
5. **Suggest hypotheses** with rationale and validation experiments
6. **Draft** Abstract, Introduction and Methodology sections
7. **Manage references** - APA list and BibTeX export; optional save to IBM Cloud Object Storage

## IBM technology used
| Service | Plan | Purpose |
|---|---|---|
| watsonx.ai Runtime + **IBM Granite** (`ibm/granite-3-8b-instruct`) | Lite | All reasoning / generation |
| Cloud Object Storage | Lite (optional) | Persist reports |
| Code Engine | Free tier (optional) | Host the app |

## Setup
1. Create an IBM Cloud account -> create **watsonx.ai Runtime** (Lite) and a **watsonx.ai project** (associate the Runtime instance in Manage -> Services).
2. Create an IBM Cloud API key (Manage -> Access (IAM) -> API keys). Copy the project ID from the project's Manage tab.
3. Install and configure:
```bash
pip install -r requirements.txt
cp .env.example .env     # fill in WATSONX_API_KEY and WATSONX_PROJECT_ID
streamlit run app.py     # web UI
# or
python cli.py "your research question"
```
Set `WATSONX_URL` to your region (e.g. `https://eu-de.ml.cloud.ibm.com`) if not us-south.

## Deploy on IBM Code Engine (optional)
```bash
ibmcloud login --sso && ibmcloud plugin install code-engine
ibmcloud ce project create --name research-agent
ibmcloud ce application create --name research-agent --build-source . \
  --port 8080 --env-from-secret research-secrets
```
(Create the secret first with `ibmcloud ce secret create --name research-secrets --from-env-file .env`.)

## Structure
```
app.json          App manifest (name, IBM services, env vars)
docs/problem_statement.pdf
docs/project_presentation.pptx
app.py            Streamlit UI
cli.py            Command-line runner
agent/llm.py      Granite wrapper (watsonx.ai)
agent/search.py   arXiv + OpenAlex retrieval
agent/tasks.py    Summarize / review / hypotheses / drafting pipeline
agent/citations.py APA + BibTeX
agent/storage.py  IBM COS upload
```
Note: always verify generated text and references against the original papers.

## Push to GitHub
```bash
cd research-agent
git init && git add . && git commit -m "Research Agent using IBM Granite"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
Never commit your `.env` (it is in `.gitignore`).
