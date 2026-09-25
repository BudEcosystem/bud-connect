# Fact-checking a researched model

The second pass of `enrich_catalog.py`'s research step. A researcher has written
`catalog/results/<slug>.json` following `RESEARCH_PROMPT.md`. A second agent then checks every
claim in that file against the web and fixes the file in place.

In the pilot this pass changed 14% of claims. About 6% of all claims were real errors: stale
status, a sibling model's benchmark, unsupported detail. It also produced one error of its own,
by deleting a true claim because the cited page didn't state it. Both failure modes matter.

## For each file

1. Read `RESEARCH_PROMPT.md`. The file must meet it.
2. Open every URL in `sources`.
3. Check every claim:
   - each sentence of `description`;
   - every item of `advantages`, `disadvantages` and `use_cases`;
   - `languages` and `website_url`;
   - every `evaluations` score.

   A claim is supported only if a page you opened states it for this exact model and version.
4. When a claim is not on the cited page, **search before removing it**. Look at the maker's
   other current pages: the models overview, the language list, the deprecations page, the
   changelog. If you find support there, add that page to `sources` and keep the claim. Remove it
   only when you cannot find support, or when a current page contradicts it.
5. Check the model's current status yourself (GA, preview, legacy, deprecated, superseded) on
   the maker's current pages, because researchers tend to trust launch posts.
6. Fix the file in place:
   - remove what is unsupported;
   - correct wrong numbers, names and dates;
   - move a non-accuracy figure (WER, Elo, speed, latency) out of `evaluations` into an
     `advantages` sentence;
   - drop scores from a blog's own test runs;
   - remove marketing superlatives and prices;
   - add every page you newly relied on to `sources`.

   Add no claim beyond what a correction needs, and keep `researched_on`.
7. Run `python3 enrich_catalog.py merge --dry-run` from `scripts/model_docs_workflow` and fix
   any INVALID line about your files.

Do not spawn sub-agents, do not run `merge` without `--dry-run`, and do not edit other files.

## Tags for reporting changes

- `UNSUPPORTED`: removed, no page supports it.
- `WRONG`: corrected, old → new.
- `WRONG_MODEL`: the claim was about a sibling, base checkpoint or predecessor.
- `STALE`: true once, contradicted by a current page.
- `MOVED`: a non-accuracy figure moved out of `evaluations`.
- `STYLE`: a superlative or price removed.
- `SOURCE`: a source added or replaced, with the claim kept.
