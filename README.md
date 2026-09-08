# Engineering Study Cards — Interactive Practice

Adaptive Streamlit study app with flashcards, multiple choice, fill-in-the-blank, mixed quizzes, spaced retrieval, concept mastery, and interactive math/vector builders.

## New interactive practice mode
Choose **Interactive Practice** in the sidebar. The app now generates randomized objective questions for:

- Dot product — enter the scalar result
- Cross product — enter the i, j, k components
- Product rule — build the rule by selecting the correct factors in four slots
- Quotient rule — build the numerator and denominator structure
- Power rule — enter the coefficient and new exponent
- Chain rule — complete the coefficient and outer exponent for randomized `(ax+b)^n` derivatives

Interactive answers count toward the current quiz score and Perfect Streak. Misses enter the same adaptive retrieval queue as the other objective modes, so they return after spacing and can generate new randomized variations.

## Study engine
- Missed questions return after 3–5 intervening questions.
- Successful delayed reviews schedule another concept variation roughly 8–12 questions later.
- Topics are interleaved where possible.
- Concept mastery requires multiple successful delayed retrievals and question variations.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```


## Cross-product visual builder + Skip
- Cross-product interactive questions now show the full i/j/k determinant, the +/−/+ expansion, and the exact two products used for each component.
- Added **Skip — Mark Needs Work** in Interactive Practice. A skipped card is recorded as a weakness and automatically queued for a spaced review after 3–5 other questions; it does not count as a submitted quiz answer.

## Rule-builder equivalence update
- Product rule now accepts any mathematically equivalent ordering of the two factors and either order of the two added product terms.
- Quotient rule now accepts either multiplication order inside each numerator product (for example `f'g` or `gf'`) while correctly preserving the subtraction order and denominator `g^2`.

- Cross product interactive practice now uses compact numeric fill-in rows instead of dropdown builders.
