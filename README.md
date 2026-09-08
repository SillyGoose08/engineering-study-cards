# Engineering Study Cards — Quiz Modes + Perfect Streaks

Adaptive Streamlit study app with four answer styles:

- **Flashcards** — Quizlet-style flip presentation with self-rating
- **Multiple Choice** — objectively graded A/B/C/D questions
- **Fill in Blank** — type simple math answers directly
- **Mixed Quiz** — uses multiple choice when options exist and fill-in for simple cards

## New in this build

- **Start a New Session** resets the timer, session score, progress, and current perfect streak.
- **Perfect Streak Record** tracks the best number of objectively graded answers answered correctly in a row.
- Flashcard self-ratings still train the weakness model but **do not affect the perfect streak**.
- Fill-in answers accept normalized spacing/case/basic notation.
- Math prompts and answers retain LaTeX formatting.
- Deck Manager can create Flashcard, Multiple Choice, and Fill in Blank cards.

## Files

Upload `app.py`, `requirements.txt`, and `README.md` to the GitHub repo root. Streamlit Community Cloud should redeploy automatically.

## Storage note

Progress is currently stored in local SQLite (`flashcards.db`). Streamlit Community Cloud may reset local files during rebuilds, so durable cloud storage is still a future upgrade.
