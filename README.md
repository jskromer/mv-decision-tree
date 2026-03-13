# M&V Planning Decision Tree

Interactive decision tree for designing Measurement & Verification (M&V) plans using the **Counterfactual Designs** framework — Boundary, Model Form, and Duration instead of protocol labels.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/jskromer/mv-decision-tree/main/app.py)
[![Run on Replit](https://replit.com/badge?caption=Run%20on%20Replit)](https://replit.com/github/jskromer/mv-decision-tree)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

| Platform | How |
|----------|-----|
| **Streamlit Community Cloud** | [share.streamlit.io](https://share.streamlit.io) → New app → point to `jskromer/mv-decision-tree`, branch `main`, file `app.py` |
| **Replit** | Click the badge above, or import from GitHub URL: `https://github.com/jskromer/mv-decision-tree` |
| **Vercel** | Not compatible — Vercel serves static/serverless, not long-running Python apps |

## Framework

Every M&V counterfactual design is defined by three dimensions:

- **Boundary** — what do you draw the measurement boundary around?
- **Model Form** — how do you construct the counterfactual? (stipulated parameters, statistical regression, engineering simulation, hybrid)
- **Duration** — how much baseline and reporting-period data is needed?

Built on the [Counterfactual Designs](https://counterfactual-designs.com) framework by Steve Kromer.

See also: [CfDesigns interactive platform](https://cfdesigns.vercel.app) · [IPMVP-aligned course](https://mv-course.vercel.app)
