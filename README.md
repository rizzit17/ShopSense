# ShopSense

Live application: [shopsense-jade.vercel.app](https://shopsense-jade.vercel.app).

Discovering different shopping personalities using machine learning. An AI academic case study, built with Python, pandas, scikit-learn, FastAPI/Pydantic, React, TypeScript, Vite, Tailwind and Recharts. ReportLab generates the academic PDF.

ShopSense converts transaction lines into customer RFM profiles, compares raw and log feature spaces, and exposes the results through an interactive analytics page. Personality names describe observed purchase behavior; they are not psychological assessments. This is an educational implementation, not a novel clustering algorithm or a production decision system.

## Dataset and verified preprocessing

[UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), Chen, D. (2015), DOI: [10.24432/C5BW33](https://doi.org/10.24432/C5BW33), CC BY 4.0. Transactions cover 1 December 2010 through 9 December 2011. The retailer sells gifts; many customers are wholesalers.

The workbook contains **541,909 lines**. Sequential exclusions:

| Stage | Excluded | Remaining |
|---|---:|---:|
| Missing CustomerID removal | 135,080 | 406,829 |
| Cancelled transactions removal | 8,905 | 397,924 |
| Non-positive Quantity or UnitPrice removal | 40 | 397,884 |
| Exact duplicate records removal | 5,192 | 392,692 |

Result: **392,692 valid lines**, **4,338 customers**, **18,532 distinct invoices**, and **£8,887,208.89 positive recorded spending**. This spending excludes returns and is not net revenue. Duplicate identity uses every original column, including Country; duplicate origin is unknown.

Recency uses elapsed whole 24-hour days relative to **2011-12-10 12:50:00**, one day after the final retained transaction. Frequency counts distinct invoices per customer, not lines. Monetary sums Quantity × UnitPrice, rounding each line to two decimal places. CustomerID is never a clustering input. The audit JSON records sequential counts and the workbook SHA-256.

## ML methodology and actual results

For every K=2..8, compare A: StandardScaler(raw RFM) against B: StandardScaler(log1p(RFM)). All candidates and the final model use K-Means++, Lloyd updates, seed 42 and n_init=20. All 4,338 customers are used for silhouette scoring without sampling. Training runs with one numerical thread.

**Selected: log RFM, K=4**. K=4 is a descriptive granularity choice after inspecting K=2..8. K=2 has the highest log-space silhouette; four clusters retain useful RFM detail with balanced groups. The elbow is gradual, and no uniquely optimal K is claimed. Log scaling creates more balanced descriptive groups. Raw scaling is not mathematically invalid; it emphasizes extreme buyers. Metrics from different geometries cannot establish an accuracy improvement. Scores are internal fit-set diagnostics, with no external ground-truth labels or temporal holdout.

| Final-model diagnostic | Value |
|---|---:|
| Silhouette | 0.3373 |
| Davies–Bouldin (lower preferred) | 1.0106 |
| Calinski–Harabasz (higher preferred) | 3328.92 |
| Inertia | 3938.6 |
| Two-component PCA variance | 93.87% |

PCA is for display only; clustering uses all three standardized log features. All customers appear on the default interactive map; optional sampling is explicit and deterministic (seed 42).

| Descriptive segment | Customers | Median recency (days) | Median frequency | Median spending |
|---|---:|---:|---:|---:|
| High-Value Champions | 709 (16.34%) | 8 | 10 | £3,722.82 |
| At-Risk Valuable Shoppers | 1,173 (27.04%) | 55 | 4 | £1,341.65 |
| Active Regular Shoppers | 839 (19.34%) | 17 | 2 | £466.70 |
| Dormant Low-Engagement Shoppers | 1,617 (37.28%) | 177 | 1 | £298.40 |

Names are derived from median RFM relative to population medians; cluster IDs have no ordinal meaning. Any retention or marketing suggestions are hypotheses, not measured outcomes.

## Setup and reproduction (PowerShell)

Tested with Python 3.13, Node 22.22.2 and scikit-learn 1.8.0. Use Node 22.12+ or a compatible newer LTS release. The Python lock file records tested direct dependency versions. Only load trusted joblib artifacts.

From the project directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
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
| GET | /api/segments/{cluster_id} | One profile, or 404 |
| GET | /api/evaluation | Metrics, K candidates, raw/log experiment and training settings |
| GET | /api/visualization | Customer PCA coordinates; sample_limit 1..10000, default 5000 |
| POST | /api/predict | {recency, frequency, monetary} through saved fitted pipeline |

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
