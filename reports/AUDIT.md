# ShopSense final engineering audit

Completed 30 October 2026. The existing architecture and real UCI workbook were preserved.

| Phase | Outcome |
|---|---|
| Repository audit | Reviewed ML scripts, artifacts, backend routes/services/schemas, frontend components/styles/contracts, report generator, README, viva notes, dependencies and original tests. |
| ML | Reprocessed the full workbook, retrained both representations at K=2..8 with consistent initialization settings, saved a complete inference pipeline and recomputed all diagnostics. |
| API | Repaired training-range warnings, artifact readiness, typed contracts, bounded sampling, finite-number validation, error serialization and configured CORS. |
| Interface | Removed fallback analytics and unsupported status badges; added truthful loading/error states, customer map, accessible selection, actual experiment/RFM tables, methodology workflow and responsive navigation. |
| Report | Generated and visually inspected seven A4 pages, verified exactly five main sections and artifact-derived tables, checked references against primary sources. |
| Verification | 37 pytest checks pass; TypeScript/Vite production build passes without bundle warnings; lint passes; Playwright/Edge browser checks pass with no page or console errors. |
| Documentation | Updated README and viva explanations; added editable student metadata, source records, dependency versions and documentation regeneration. |

## Main defects resolved

- README reported 19,788 orders; distinct valid invoices actually total 18,532. Frequency is independently reconciled to customer invoice counts.
- UI narratives used 0.3375 silhouette / 1.0086 Davies-Bouldin while the saved final model yielded 0.3373 / 1.0106. Candidate training used 10 initializations and final training 20. Both now use 20 and their selected-K outputs match.
- UI showed fixed customer, spend, cleaning and PCA values while the API was unavailable. Those fallbacks are removed and a retry state replaces unavailable analytics.
- Prediction limits were approximated constants and missed some values just outside training ranges. Bounds are now recorded from the actual RFM table, including lower bounds.
- Separate hand-coded prediction transforms could drift. Inference now loads a fitted log1p -> StandardScaler -> K-Means pipeline, tested against every stored customer assignment.
- Visualization sampling accepted negative or excessive limits; limits now validate at 1..10000 and default requests return all 4,338 customers.
- CORS ignored configured origins and allowed every origin; configuration is now honored.
- Health returned healthy without checking artifacts; it now checks overview, evaluation, coordinates and inference readiness. Missing artifacts return 503.
- Non-finite JSON inputs could create validation errors that themselves failed JSON serialization; a bounded validation response returns 422 without echoing unsafe inputs.
- Segment cards were mouse-only and their inspection drawer could disagree with map selection. Cards support keyboard selection and use one shared selected-cluster state.
- Predictor silently truncated fractional frequency and retained results after presets changed. Frequency requires a safe integer; changing inputs/presets clears previous results.
- Tablet navigation overflowed at 768px; browser testing caught and verified the fix.
- The evaluation presentation overstated raw RFM as mathematically flawed and K=4 as objectively optimal. It now explains geometry, K=2's higher silhouette and the judgment behind four descriptive groups.
- Report used literal LaTeX in a renderer that does not typeset it and included invented student/course details. The new generator uses readable expressions and four clearly marked metadata fields.
- Dataset citation was confused with the introductory paper. The report distinguishes Chen (2015) dataset attribution from Chen, Sain and Guo (2012).
- Parquet support was omitted from dependencies; pyarrow is now declared. Native frontend build and browser execution were validated outside the restricted subprocess sandbox.

## Verified data and model

Raw lines 541,909; retained lines 392,692; customers 4,338; distinct completed invoices 18,532; positive recorded spending GBP 8,887,208.89.

Chosen representation: standardized log1p RFM, K=4, seed 42, n_init=20, all-customer silhouette without sampling. Silhouette 0.3373; Davies-Bouldin 1.0106; Calinski-Harabasz 3328.92; inertia 3938.60; PCA variance retained 93.87%.

Cluster populations: 709, 1,173, 839 and 1,617 customers. Means, medians, proportions, ranges and candidate diagnostics are in `ml/artifacts/*.json`.

## Commands actually exercised

```powershell
python ml/download_data.py
python ml/preprocess.py
python ml/train.py
python ml/evaluate.py
python reports/generate_report.py
python reports/update_documentation.py
python -m pytest -q
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
cd frontend
npm run build
npm run lint
npm run dev -- --host 127.0.0.1
```

With servers running, `python tests/browser_check.py` verified real map points, selection, experiment tabs, RFM charts, predictions, presets, outlier warnings, offline states and overflow at 1440, 768 and 390px. The checks use installed Microsoft Edge through Playwright. Browser screenshots and console results are under `tmp/browser/`; rendered report pages are under `tmp/pdfs/` (both ignored by Git).

The ML regression independently recomputes every customer's RFM, checks all saved assignments, recalculates metrics and refits the model with the same seed. The report regression checks seven pages, A4 geometry, all five required headings, result values, figures and text within page bounds. Every report page was also visually inspected.

## Remaining limits and submission step

No engineering blocker remains in this environment. K=4 is a descriptive choice, not a unique statistical optimum. One old retailer dataset, missing identifiers, returns exclusion and absent temporal/external validation limit generalization. Suggested business actions have not been tested. The Python version snapshot pins direct dependencies, not every transitive dependency.

Fill student name, registration number, faculty and submission date in `reports/student.json`, then regenerate the PDF before uploading to VTOP. The project does not upload the report to VTOP.

## Deployment scope

Vercel configuration and a serverless entrypoint were added concurrently by another process during this audit. Hosted deployment was not executed or verified here. The active frontend deliberately uses API responses and exposes failures; an unused exported fallback data file is not imported or used for inference. Local startup and browser checks are the verified delivery path.
