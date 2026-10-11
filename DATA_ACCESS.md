# Data access

This repository contains no data. The analyses read MIMIC-III directly from Google BigQuery, which requires credentialed access.

## What you need

1. **A PhysioNet account** at https://physionet.org, with credentialing completed.
2. **Human subjects research training**, as required by PhysioNet for credentialed datasets.
3. **The signed data use agreement** for the MIMIC-III Clinical Database v1.4 (https://doi.org/10.13026/C2XW26).
4. **BigQuery access to the `physionet-data` datasets**, requested from the MIMIC-III project page on PhysioNet once you are credentialed.
5. **A Google Cloud project of your own**, used to run queries. Its ID replaces `YOUR-GCP-PROJECT-ID` in each notebook (see the main README).

Follow PhysioNet's current instructions for each step, since the process may change.

## Tables used

| Table | Used for |
|---|---|
| `physionet-data.mimiciii_notes.noteevents` | Note text (read in memory only), `CGID`, `HADM_ID`, `SUBJECT_ID`, `ROW_ID`, `CHARTDATE` |
| `physionet-data.mimiciii_clinical.diagnoses_icd` | Principal diagnosis (`SEQ_NUM = 1`) |

## Obligations that carry over to you

- Do not share MIMIC-III data, including row-level values derived from it, with anyone who is not credentialed for it.
- Do not commit notebook outputs. Clear them before every commit and run `python scripts/check_before_push.py`.
- Do not send MIMIC-III data to external services that are not covered by the data use agreement.
