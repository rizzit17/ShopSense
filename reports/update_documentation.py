"""Regenerate README results and viva notes from the same model artifacts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
a=read('data/processed/preprocessing_audit.json');m=read('ml/artifacts/evaluation_metrics.json');profiles=read('ml/artifacts/cluster_profiles.json');exp=read('ml/artifacts/experiment_comparison.json')
rows='\n'.join(f'| {s["name"]} | {s["count"]:,} ({s["percentage"]}%) | {s["Recency_median"]:g} | {s["Frequency_median"]:g} | £{s["Monetary_median"]:,.2f} |' for s in profiles)
readme=f'''# ShopSense

Discovering different shopping personalities using machine learning. An AI academic case study for VIT Vellore, built with Python, pandas, scikit-learn, FastAPI/Pydantic, React, TypeScript, Vite, Tailwind and Recharts. ReportLab generates the academic PDF.

ShopSense converts transaction lines into customer RFM profiles, compares raw and log feature spaces, and exposes the results through an interactive analytics page. Personality names describe observed purchase behavior; they are not psychological assessments. This is an educational implementation, not a novel clustering algorithm or a production decision system.

## Dataset and verified preprocessing

[UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), Chen, D. (2015), DOI: [10.24432/C5BW33](https://doi.org/10.24432/C5BW33), CC BY 4.0. Transactions cover 1 December 2010 through 9 December 2011. The retailer sells gifts; many customers are wholesalers.

The workbook contains **{a['raw_rows']:,} lines**. Sequential exclusions:

| Stage | Excluded | Remaining |
|---|---:|---:|
'''+'\n'.join(f'| {s["name"]} | {s["excluded"]:,} | {s["remaining"]:,} |' for s in a['steps'])+f'''

Result: **{a['total_clean_rows']:,} valid lines**, **{a['unique_customers']:,} customers**, **{a['total_orders']:,} distinct invoices**, and **£{a['total_revenue_gbp']:,.2f} positive recorded spending**. This spending excludes returns and is not net revenue. Duplicate identity uses every original column, including Country; duplicate origin is unknown.

Recency uses elapsed whole 24-hour days relative to **{a['reference_date']}**, one day after the final retained transaction. Frequency counts distinct invoices per customer, not lines. Monetary sums Quantity × UnitPrice, rounding each line to two decimal places. CustomerID is never a clustering input. The audit JSON records sequential counts and the workbook SHA-256.

## ML methodology and actual results

For every K=2..8, compare A: StandardScaler(raw RFM) against B: StandardScaler(log1p(RFM)). All candidates and the final model use K-Means++, Lloyd updates, seed 42 and n_init=20. All {m['n_customers']:,} customers are used for silhouette scoring without sampling. Training runs with one numerical thread.

**Selected: log RFM, K={m['selected_k']}**. {m['selection_reason']} Log scaling creates more balanced descriptive groups. Raw scaling is not mathematically invalid; it emphasizes extreme buyers. Metrics from different geometries cannot establish an accuracy improvement. Scores are internal fit-set diagnostics, with no external ground-truth labels or temporal holdout.

| Final-model diagnostic | Value |
|---|---:|
| Silhouette | {m['silhouette_score']} |
| Davies–Bouldin (lower preferred) | {m['davies_bouldin_index']} |
| Calinski–Harabasz (higher preferred) | {m['calinski_harabasz_score']} |
| Inertia | {m['inertia']} |
| Two-component PCA variance | {m['pca_total_variance_pct']}% |

PCA is for display only; clustering uses all three standardized log features. All customers appear on the default interactive map; optional sampling is explicit and deterministic (seed 42).

| Descriptive segment | Customers | Median recency (days) | Median frequency | Median spending |
|---|---:|---:|---:|---:|
{rows}

Names are derived from median RFM relative to population medians; cluster IDs have no ordinal meaning. Any retention or marketing suggestions are hypotheses, not measured outcomes.

## Setup and reproduction (PowerShell)

Tested with Python 3.13, Node 22.22.2 and scikit-learn {m['sklearn_version']}. Use Node 22.12+ or a compatible newer LTS release. The Python lock file records tested direct dependency versions. Only load trusted joblib artifacts.

From the project directory:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements-lock.txt
python ml/download_data.py
python ml/preprocess.py
python ml/train.py
python ml/evaluate.py
python reports/generate_report.py
python -m pytest -q
cd frontend
npm ci
npm run build
npm run lint
```

The downloader uses the official UCI archive when the workbook is absent. Preprocessing and training overwrite derived artifacts. Regenerate after changing data or library versions; restart the API after regeneration because it caches artifacts.

Start the backend in one terminal from the project directory:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Start the frontend in a second terminal:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1
```

Open [ShopSense](http://127.0.0.1:5173/) or [API documentation](http://127.0.0.1:8000/docs). Vite proxies `/api` to `127.0.0.1:8000` during development and preview. For a separate frontend host set `VITE_API_BASE` in `frontend/.env.local` and configure `CORS_ORIGINS` in the backend process environment. `.env.example` is documentation; Python does not automatically load it.

## API contracts

| Method | Path | Behavior |
|---|---|---|
| GET | /api/health | Checks dataset, model and visualization readiness; missing artifacts return 503 |
| GET | /api/overview | Counts, spending, date horizon, sequential cleaning audit |
| GET | /api/segments | Profiles, sizes, proportions and mean/median RFM |
| GET | /api/segments/{{cluster_id}} | One profile, or 404 |
| GET | /api/evaluation | Metrics, K candidates, raw/log experiment and training settings |
| GET | /api/visualization | Customer PCA coordinates; sample_limit 1..10000, default 5000 |
| POST | /api/predict | {{recency, frequency, monetary}} through saved fitted pipeline |

Prediction requires finite numeric recency >=0, integer frequency >=1 and monetary >=0.01. Missing, negative, non-finite, malformed and extra inputs return 422. Valid inputs outside observed training bounds still receive a prediction with a warning; these are extrapolations. There are no confidence probabilities. API requests never retrain the model. Unexpected artifact-processing failures return 500 without leaking local paths.

## Academic report and viva

Final PDF: `reports/ShopSense_AI_Case_Study.pdf`, seven A4 pages with exactly five main sections: Introduction; Literature; Problem Statement / Objectives; Methodology / Implementation; Results. The Results section includes limitations and future work. Three verified academic sources plus dataset attribution appear in Literature. Source verification links are in `reports/SOURCES.md`.

Edit `reports/student.json` to replace the four clearly marked student metadata placeholders. Then run:

```powershell
python reports/generate_report.py
```

See `reports/VIVA_NOTES.md` for natural-language explanations and ten faculty questions. To refresh documentation tables after retraining:

```powershell
python reports/update_documentation.py
```

## Verification

`python -m pytest -q` checks API validation, audited counts, invoice-level frequency, all customer RFM values, saved-pipeline assignments, metric recomputation, deterministic refitting, training boundaries, missing artifacts and paths independent of the working directory. Temporary files stay under `tmp/`.

For optional browser testing, install Playwright in the chosen environment and use an installed Microsoft Edge browser. With both servers running:

```powershell
python -m pip install playwright
python tests/browser_check.py
```

This verifies all 4,338 plotted customers, keyboard-accessible segment selection, evaluation tabs, saved-model prediction, presets, extrapolation warnings, responsive overflow at 390/768px, and API-unavailable behavior. Screenshots and console results go to `tmp/browser/`. PDF pages can be rendered with PyMuPDF for visual inspection. See `reports/AUDIT.md` for the final engineering audit.

## Limitations

One retailer and an old observation window limit generalization. Missing customer identifiers cause exclusions. Dropping cancellations means the monetary feature is gross positive purchase spending rather than net sales. Exact duplicate removal is an assumption. RFM omits product preferences and within-window temporal changes. K-Means assumes Euclidean, roughly spherical groups. K=4 is a reasoned descriptive choice, not a proven unique optimum. No external label validation, seed-stability study, future-churn evaluation or intervention trial has been performed.
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
q=[('What is ShopSense?','It groups customers with similar purchase history and explains those groups using RFM. Shopping personality means observed behavior, not psychology.'),('What problem does it solve?','Invoices contain many item lines. We summarize each customer once so patterns are visible without manually reading transaction logs.'),('Which dataset is used?',f'UCI Online Retail, donated by Daqing Chen in 2015. The records cover December 2010 to December 2011. There are {a["raw_rows"]:,} original lines.'),('Why RFM?','It is compact and easy to explain: how recently a person purchased, how many distinct orders they completed and how much they spent in the window.'),('What does K-Means do?','It assigns each customer to the closest of K centroids, then updates the centroids to reduce squared distances.'),('What is unsupervised learning?','Learning groups from features without known correct category labels. We have no target shopping-personality column.'),('Why log-transform and scale?','Log1p compresses extreme values. Scaling prevents GBP amounts from dominating solely because of units. Both change the distance geometry.'),('How was K selected?',m['selection_reason']),('What does silhouette mean?',f'It compares within-group closeness with distance to the nearest alternative group. The selected model scores {m["silhouette_score"]}; overlap remains.'),('How are segments interpreted?','After fitting, compare group medians with population medians. Names follow measured RFM behavior, never fixed cluster IDs.'),('What did the experiment show?','Raw scaling isolates small extreme-buyer groups and has higher silhouette in its own geometry. Log scaling gives more balanced descriptive groups. This does not prove higher accuracy.'),('What is novel?','The contribution is the reproducible integration: audited cleaning, a controlled feature comparison, interpretable labels, API inference and interactive inspection. The algorithms are established.'),('What are the limitations?','One old retailer dataset, missing IDs, positive purchases rather than net spending, compressed temporal information, overlapping clusters and no independent future-outcome validation.')]
notes='# ShopSense viva notes\n\nUse these as explanations, not a memorized script.\n\n'+'\n\n'.join(f'## {i}. {title}\n\n{answer}' for i,(title,answer) in enumerate(q,1))
notes+='\n\n## 14. Ten likely faculty questions\n\n'
qa=[('Why no accuracy or F1?','There are no ground-truth labels. We report internal clustering metrics rather than classification scores.'),('Why not K=2?',f'K=2 has the higher log silhouette, {m["candidate_k_evaluation"][0]["silhouette"]}. Four groups provide more behavioral detail. This is a judgment, not a mathematical proof.'),('Is raw RFM wrong?','No. It emphasizes extreme shoppers. That is useful for some questions, but less useful for differentiating typical customers here.'),('Do line items count as orders?','No. Frequency uses the count of unique completed invoices per customer.'),('What is the recency reference?',f'{a["reference_date"]}, one day after the latest valid purchase. Recency is elapsed whole 24-hour days.'),('Does monetary mean net revenue?','No. Returns and cancellations are excluded, so it is positive recorded spending within the dataset window.'),('What happens above the training range?','The fitted pipeline still predicts a group, and the response warns that the input is outside observed bounds. It does not produce confidence probabilities.'),('Why use PCA?','To display three scaled log features in two dimensions. K-Means does not use the reduced coordinates.'),('How do you prove inference is consistent?','The test loads the saved pipeline and reproduces every stored customer assignment, then recomputes metrics and refits with the same seed.'),('What would you improve next?','Use temporal validation, compare stability across seeds and resampling, compare clustering methods, and evaluate independent future behavior.')]
notes+='\n\n'.join(f'### Q{i}. {title}\n\n{answer}' for i,(title,answer) in enumerate(qa,1))
notes+=f'\n\n## Verified numbers for the demonstration\n\n{a["total_clean_rows"]:,} valid lines; {a["unique_customers"]:,} customers; {a["total_orders"]:,} invoices; £{a["total_revenue_gbp"]:,.2f} spending. K={m["selected_k"]}, silhouette {m["silhouette_score"]}, DB {m["davies_bouldin_index"]}, CH {m["calinski_harabasz_score"]}.\n\n| Segment | Customers | R median | F median | M median |\n|---|---:|---:|---:|---:|\n'+rows+'\n'
(ROOT/'reports/VIVA_NOTES.md').write_text(notes,encoding='utf-8')
print('Updated README.md and reports/VIVA_NOTES.md from artifacts')
