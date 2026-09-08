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

## Formatting readability fix
- Long answer choices are stacked vertically instead of squeezed into two columns.
- Prose answer choices keep normal spacing while math fragments render inline.
- Raw powers such as `x^2` in prose questions now display as superscript math.
- Natural-language integral prompts now render the integral itself properly.

## Smart distractor + stable answer-bank fix
- Generated multiple-choice distractors now come from curated concept families, so answers are plausible for the question.
- Quadric-surface questions now compare related surfaces instead of unrelated vector/calculus terms.
- Generated answer banks are frozen for the current card and no longer change when a radio choice reruns Streamlit.
