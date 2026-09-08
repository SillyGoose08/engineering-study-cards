# Engineering Study Cards — Phase 1

Adaptive Streamlit flashcard app that tracks missed cards and automatically prioritizes weak material.

## Core behavior
- Study modes: Weakest First, Missed Only, Random
- Persistent SQLite attempt history
- Per-card weakness score and mastery score
- Topic mastery visuals
- Refined study set built automatically from missed/unseen cards
- Confidence rating after each attempt
- Deck manager for adding custom cards
- Seeded with Calc 3 recognition cards

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

For Streamlit Cloud, put `app.py` and `requirements.txt` in the repo root and deploy `app.py`.
