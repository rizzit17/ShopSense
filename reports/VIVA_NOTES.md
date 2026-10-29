# ShopSense viva notes

Use these as explanations, not a memorized script.

## 1. What is ShopSense?

It groups customers with similar purchase history and explains those groups using RFM. Shopping personality means observed behavior, not psychology.

## 2. What problem does it solve?

Invoices contain many item lines. We summarize each customer once so patterns are visible without manually reading transaction logs.

## 3. Which dataset is used?

UCI Online Retail, donated by Daqing Chen in 2015. The records cover December 2010 to December 2011. There are 541,909 original lines.

## 4. Why RFM?

It is compact and easy to explain: how recently a person purchased, how many distinct orders they completed and how much they spent in the window.

## 5. What does K-Means do?

It assigns each customer to the closest of K centroids, then updates the centroids to reduce squared distances.

## 6. What is unsupervised learning?

Learning groups from features without known correct category labels. We have no target shopping-personality column.

## 7. Why log-transform and scale?

Log1p compresses extreme values. Scaling prevents GBP amounts from dominating solely because of units. Both change the distance geometry.

## 8. How was K selected?

K=4 is a descriptive granularity choice after inspecting K=2..8. K=2 has the highest log-space silhouette; four clusters retain useful RFM detail with balanced groups. The elbow is gradual, and no uniquely optimal K is claimed.

## 9. What does silhouette mean?

It compares within-group closeness with distance to the nearest alternative group. The selected model scores 0.3373; overlap remains.

## 10. How are segments interpreted?

After fitting, compare group medians with population medians. Names follow measured RFM behavior, never fixed cluster IDs.

## 11. What did the experiment show?

Raw scaling isolates small extreme-buyer groups and has higher silhouette in its own geometry. Log scaling gives more balanced descriptive groups. This does not prove higher accuracy.

## 12. What is novel?

The contribution is the reproducible integration: audited cleaning, a controlled feature comparison, interpretable labels, API inference and interactive inspection. The algorithms are established.

## 13. What are the limitations?

One old retailer dataset, missing IDs, positive purchases rather than net spending, compressed temporal information, overlapping clusters and no independent future-outcome validation.

## 14. Ten likely faculty questions

### Q1. Why no accuracy or F1?

There are no ground-truth labels. We report internal clustering metrics rather than classification scores.

### Q2. Why not K=2?

K=2 has the higher log silhouette, 0.4328. Four groups provide more behavioral detail. This is a judgment, not a mathematical proof.

### Q3. Is raw RFM wrong?

No. It emphasizes extreme shoppers. That is useful for some questions, but less useful for differentiating typical customers here.

### Q4. Do line items count as orders?

No. Frequency uses the count of unique completed invoices per customer.

### Q5. What is the recency reference?

2011-12-10 12:50:00, one day after the latest valid purchase. Recency is elapsed whole 24-hour days.

### Q6. Does monetary mean net revenue?

No. Returns and cancellations are excluded, so it is positive recorded spending within the dataset window.

### Q7. What happens above the training range?

The fitted pipeline still predicts a group, and the response warns that the input is outside observed bounds. It does not produce confidence probabilities.

### Q8. Why use PCA?

To display three scaled log features in two dimensions. K-Means does not use the reduced coordinates.

### Q9. How do you prove inference is consistent?

The test loads the saved pipeline and reproduces every stored customer assignment, then recomputes metrics and refits with the same seed.

### Q10. What would you improve next?

Use temporal validation, compare stability across seeds and resampling, compare clustering methods, and evaluate independent future behavior.

## Verified numbers for the demonstration

392,692 valid lines; 4,338 customers; 18,532 invoices; £8,887,208.89 spending. K=4, silhouette 0.3373, DB 1.0106, CH 3328.92.

| Segment | Customers | R median | F median | M median |
|---|---:|---:|---:|---:|
| High-Value Champions | 709 (16.34%) | 8 | 10 | £3,722.82 |
| At-Risk Valuable Shoppers | 1,173 (27.04%) | 55 | 4 | £1,341.65 |
| Active Regular Shoppers | 839 (19.34%) | 17 | 2 | £466.70 |
| Dormant Low-Engagement Shoppers | 1,617 (37.28%) | 177 | 1 | £298.40 |
