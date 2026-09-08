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

## Plausible-answer + LaTeX rendering fix
- Multiple-choice math choices now render through Markdown/LaTeX, so `$...$` delimiters do not appear literally.
- Point-normal, line-form, plane-parallel, and normal-vector questions now use realistic line/plane distractors.
- Formula questions no longer fall back to obvious nonsense such as `0` and `1` unless that answer type genuinely fits.
- Placeholder choices such as `Choice 3` were removed.

## Ellipsoid + Greek-symbol rendering fix
- Multi-term equations such as `x^2/9+y^2/4+z^2=1` now render as separate fractions instead of a nested fraction.
- `theta` and `pi` inside prose answer choices now render as Greek symbols.

## Canonical graph-equation rendering fix
- Added explicit LaTeX mappings for circle, sphere, ellipsoid, helix, and twisted-cubic equations.
- The ellipsoid choice now renders as separate x, y, and z terms instead of being misread by the generic fraction parser.

## Formula-choice Greek symbol fix
- Formula-like multiple-choice answers now render as one coherent LaTeX expression even when they contain spaces.
- `theta` and `pi` inside formulas now render as Greek symbols.
- The standard dot-product angle formula now has an explicit canonical LaTeX form.

## Wrong-answer explanations
- Incorrect multiple-choice answers now show a concise explanation of the correct answer.
- High-value Calc 3 recognition rules are included for vectors, dot/cross products, lines/planes, quadrics, graph matching, critical numbers, and polar coordinates.
- Correct answers remain fast and uncluttered.

## Question Browser + Custom Quiz Builder
- Added a Question Browser tab with exam, subject, topic, type, and text-search filters.
- Browse one question at a time in its actual presentation format, including graph cards and MC answer banks.
- Reveal the correct answer/explanation only when wanted.
- Add/remove questions while browsing and launch the selected set as a custom quiz.
- Custom quizzes preserve selection order, do not repeat questions, and show a completion score.

## Question Browser sorting hotfix 2
Replaced tuple-based natural sort keys with string-only zero-padded keys for compatibility with pandas on Python 3.14.

## Scrollable all-question browser
- Question Browser now shows every matching question in one continuous scrollable list.
- Each question is previewed in its study presentation format.
- Every card has a one-click Add / Added button for the custom quiz builder.
- Filters and search still work, and the custom quiz can be launched from the top or bottom of the browser.

## Exam 1 calculation practice
- Added 10 numerical dot-product calculation questions to §12.3.
- Added 10 numerical cross-product calculation questions to §12.4.
- Each has controlled plausible answer choices and calculation-specific wrong-answer explanations.
- These appear automatically under Calc 3 — Exam 1 and in the scrollable Question Browser.
