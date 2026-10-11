# Expected numbers

These are the values reported in the manuscript, with the extra digits printed by the notebooks. A correct run of the notebooks in `notebooks/` should reproduce them.

Values marked **exact** do not depend on row order and should match to the last digit. Values marked **seeded** depend on random draws; see "Reproducibility of seeded results" in the main README.

## Study 1: does length track content?

Corpus: resident progress notes, ISERROR-flagged notes retained.

| Quantity | Value | Type |
|---|---|---|
| Notes / authors (CGID) | 62,682 / 435 | exact |
| Notes missing a CGID | 0 | exact |
| ISERROR-flagged notes retained | 113 (0.18%) | exact |
| Word count min / p25 / median / p75 / max | 1 / 544 / 720 / 897 / 2,745 | exact |
| Notes under 10 words | 18 | exact |
| Distinct content-proxy terms min / median / max | 0 / 11 / 29 (list size 54) | exact |
| Notes with zero proxy terms | 36 (0.06%) | exact |
| r, word count vs distinct proxy terms | 0.695 (0.6953) | exact |
| r squared | 0.484 (0.4835) | exact |
| 95% CI for r, resampling authors, 1,000 replicates, seed 2026 | 0.680 to 0.710 (bootstrap mean 0.6951, SD 0.0078) | seeded |
| Fixed-content stratum | 11 terms, n = 5,999 | exact |
| p90 / p10 length ratio at 11 terms | 1.93x (1.9288) | exact |
| p75 / p25 length ratio at 11 terms | 1.41x (1.4101) | exact |
| p90 / p10 range across strata of 2 to 22 terms | 1.74x to 2.19x (21 strata, n = 97 to 5,999; peak at 6 terms) | exact |
| Single-term stratum, reported separately (floor effect) | 3.78x, n = 317, p10 = 88 words | exact |
| r without the 10 action verbs (44 terms) | 0.641 (0.6409); r squared 0.411; change in r -0.054 | exact |
| Median proxy terms by length decile, shortest to longest | 4, 7, 9, 10, 10, 11, 12, 13, 13, 15 | exact |
| Notes with 20 or more proxy terms | 787 (1.26%) | exact |

## Study 2: does length cluster by author within diagnosis?

| Quantity | Value | Type |
|---|---|---|
| Notes loaded / after dropping missing CGID, HADM_ID or TEXT | 62,682 / 62,214 (468 dropped), 433 authors | exact |
| Ten most frequent principal diagnoses, before the five-note filter | 20,723 notes, 349 authors | exact |
| **Analysis cohort** | **20,581 notes, 266 physicians, 10 diagnoses** | exact |
| Admissions / patients in cohort | 1,163 / 1,039 | exact |
| Notes per physician | median 62, IQR 35 to 112, range 5 to 342 | exact |
| Author-admission pairs | 3,596; 81.2% contain more than one note | exact |
| Author / residual variance, single author intercept (words squared) | 16,002.5 / 55,182.4 | exact |
| **Pooled ICC (primary)** | **0.225 (0.2248)** | exact |
| 95% CI for the ICC, resampling physicians, 1,000 replicates, seed 2026 | 0.189 to 0.257 (bootstrap mean 0.2216, SD 0.0172) | seeded |
| Admission nested within author: author / admission / residual share | 0.187 / 0.244 / 0.568 | exact |
| Admission model variances (words squared) | 13,291 / 17,337 / 40,294 | exact |
| Moment decomposition, author share | 0.249 | exact |
| One note per author-admission, earliest by ROW_ID | 0.292 (n = 3,596) | exact |
| One note per author-admission, random, seeds 0 to 19 | mean 0.201, SD 0.009, middle 90% 0.184 to 0.213 | seeded |
| ICC on log word count | 0.195 (0.1953) | exact |
| ICC excluding notes under 10 words, and under 50 words | 0.225 (0.2251), n = 20,580 in both | exact |
| ROW_ID vs CHARTDATE rank correlation within admission | median 0.987 (835 admissions) | exact |
| Physician mean centered length p10 / p25 / median / p75 / p90 | -144 / -78 / +6 / +100 / +190 words | exact |
| p90 minus p10 physician difference | 334 words | exact |
| Within / between physician q75 / q25 ratio (physicians with 5 or more notes in a diagnosis) | 1.31x / 1.32x | exact |
| Per-diagnosis ICC range, single author intercept | 0.248 to 0.439 | exact |

### Per-diagnosis results

Single-intercept fits absorb admission-level variance into the author term, so these values are likely overestimates, and their ordering is not interpreted.

| ICD-9 | Diagnosis | Notes | Physicians | ICC |
|---|---|---|---|---|
| 51884 | Acute and chronic respiratory failure | 1,208 | 113 | 0.248 |
| 5070 | Food or vomit pneumonitis | 1,108 | 140 | 0.251 |
| 0389 | Septicemia, not otherwise specified | 6,344 | 239 | 0.288 |
| 42823 | Acute on chronic systolic heart failure | 1,123 | 113 | 0.290 |
| 51881 | Acute respiratory failure | 4,729 | 210 | 0.312 |
| 41071 | Subendocardial infarction, initial episode | 1,630 | 115 | 0.337 |
| 486 | Pneumonia, organism not otherwise specified | 1,671 | 169 | 0.344 |
| 42833 | Acute on chronic diastolic heart failure | 1,040 | 127 | 0.355 |
| 5770 | Acute pancreatitis | 850 | 86 | 0.376 |
| 03842 | E. coli septicemia | 878 | 101 | 0.439 |

## If your numbers differ

| You see | Likely cause |
|---|---|
| 62,569 notes and 434 authors in Study 1 | The query contains `AND ISERROR IS NULL`. That is a superseded cohort; the analysis retains ISERROR-flagged notes. |
| An ICC interval of 0.187 to 0.255 | A 200-replicate bootstrap from an earlier run. The reported interval uses 1,000 replicates. |
| Random-draw ICCs that change between runs | Rows were not sorted by ROW_ID before the seeded step. |
| A cell stops with `STOP:` | The notebook was not run from the top in a fresh session. |
