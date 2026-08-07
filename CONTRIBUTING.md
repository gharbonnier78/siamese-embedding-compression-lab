# Contributing

Contributions that improve correctness, reproducibility or experimental controls are
welcome.

Before proposing a change:

1. keep TRAIN, VALIDATION and TEST roles explicit;
2. do not select models, seeds or deployable thresholds using TEST labels;
3. distinguish observed, derived and declared evidence in replay artifacts;
4. add or update tests for changed behavior;
5. run `ruff check src tests scripts` and
   `python -m unittest discover -s tests -v`.

Please keep pull requests bounded to one scientific or engineering question. Report all
predeclared seeds and controls; do not retain only the best run. Synthetic smoke results
must never be presented as biometric evidence.

Do not commit LFW images, downloaded datasets, face embeddings, credentials or local
feature caches. New datasets must have documented provenance and redistribution terms.

