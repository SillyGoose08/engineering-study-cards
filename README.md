# Engineering Study Cards — Complete Calculus Curriculum

This build expands the adaptive study deck to cover **Calculus Chapters 1–17**, while preserving the visual UI, adaptive weakness tracking, quiz modes, streaks, and concept-aware fill-in grading.

## Curriculum
- Chapters 1–6: Calculus I foundations
- Chapters 7–11: Calculus II integration, differential equations, parametric/polar, sequences and series
- Chapters 12–16: Calculus III / vector calculus
- Chapter 17: second-order differential equations

Cards emphasize **Recognition → Setup/Method → Calculation** so the app trains method selection as well as computation.

Deploy by replacing `app.py`, `requirements.txt`, and `README.md` in the Streamlit repo root.

## Visual graph matching
Multiple-choice graph-to-equation practice covers circle, sphere, ellipsoid, helix, and twisted cubic in the relevant UNM Calc 3 Exam 1 sections.

## Session rotation fix
Cards no longer repeat within a study session while unseen eligible cards remain. Weakest First still prioritizes weak material, but now draws from a broader unseen pool for better coverage.

## Question-format update
Mixed Quiz is now primarily multiple choice. Only short recall answers of roughly 1–4 typed characters use fill-in-the-blank. Recognition cards without stored choices receive dynamically generated same-topic distractors. Common symbols such as theta and pi render as mathematical notation in question text.

## Regex hotfix
Fixed the math-notation replacement crash caused by Python interpreting LaTeX backslashes such as `\pi` as regex replacement escapes.
