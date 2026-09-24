# Researching a catalog model

This is the brief for the research step of `enrich_catalog.py`. An agent with web search and page
fetching is handed one or more entries from `catalog/targets.json`. For each one it writes
`catalog/results/<slug>.json`, then `enrich_catalog.py merge` validates the file and copies it to
every URI in the group.

What you write is shown to Bud users choosing a model, next to its price and routes. A wrong
claim is worse than a missing one: `status: "insufficient_sources"` is a correct answer.

## Input

Each target looks like this:

```json
{
  "slug": "claude-sonnet-4-5",
  "canonical": "claude-sonnet-4-5",
  "kind": "chat",
  "uris": ["anthropic/claude-sonnet-4-5", "bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0", "..."],
  "facts": {"providers": [...], "modality": [...], "endpoints": [...],
            "max_input_tokens": [...], "max_output_tokens": [...], "deprecation_date": [...]}
}
```

- `uris` are the same model offered by different hosts, regions or dated snapshots. Describe the
  model, not any one host. The part after the first `/` is the id the host's API takes.
- `kind` is what Bud serves it as: `chat`, `embedding`, `image`, `tts` (text to speech),
  `stt` (speech to text) or `rerank_moderation`.
- `facts` come from Bud's catalog and are authoritative. Do not restate a different context
  window, output limit or modality. If a source disagrees, keep the catalog's value and say so
  in `notes`.

## How to research

1. Identify exactly which model this is. Short or generic ids need care: `aws_polly/neural` is
   Amazon Polly's Neural voice engine; `deepgram/base-phonecall` is Deepgram's Base model tuned
   for phone calls. If you cannot tell which model an id refers to, stop and return
   `insufficient_sources`.
2. Read the **maker's** own pages first: the model card or docs page, the launch post, the
   model overview table. Then the **host's** page (Bedrock, Azure, Vertex, Fireworks) if the
   maker has none. Third-party pages (the Hugging Face card of an open-weight model, a paper,
   an independent benchmark such as Artificial Analysis or LMArena) come last.
3. Open every page you rely on. A search snippet is not a source.
4. Make sure a page is about this exact model and version, not a sibling. Sonnet 4.5 benchmarks
   are not Sonnet 4.6 benchmarks, and "Nova 3" is not "Nova 3 Medical".

## What to write

- `description` (2–4 sentences, 40–1200 characters): what the model is, who made it, what it is
  for, and what sets it apart. Plain and factual. Mention release or preview status when it
  matters, and say so plainly if the maker has marked the model legacy, deprecated or superseded.
- `advantages` (1–6 items): strengths a source states. Put the evidence in the sentence, e.g.
  "Scores 77.2% on SWE-bench Verified", not "excellent at coding".
- `disadvantages` (0–5 items): real limitations a source states or that follow directly from the
  facts, such as preview status, a knowledge cutoff, no audio input, English only, or being
  superseded. Do not invent weaknesses to fill the list. An empty list is fine.
- `use_cases` (1–6 items): concrete tasks the model is built or documented for.
- `evaluations`: benchmark scores the maker or a reputable evaluator published for **this exact
  model**. Each entry names the page it came from in `source`, and that URL must also appear in
  `sources`. Leave the list empty rather than guess.
  - Only accuracy-style scores where **higher is better**, between 0 and 100 (percentages as
    0–100, e.g. MMLU 85.9). Bud shows every entry on a leaderboard as an accuracy score.
  - Not here: word error rate, Elo or arena ratings, speed, latency or price. Such a figure can
    go in an `advantages` sentence with its source, e.g. "Deepgram reports a 3.44% median WER on
    medical audio".
  - Use the maker's own numbers, or a named leaderboard (Artificial Analysis, LMArena, MTEB). Do
    not use a blog or review site's own test runs.
- `languages`: languages a source names for this model, as English names ("English", "Spanish").
  List them if there are up to about 100. If a source gives only a count ("99 languages"), leave
  the list empty and put the count in the description. For chat models, list languages only if
  the maker states them.
- `website_url`: the maker's page for this model (model card or docs), or null.
- `github_url`: only for a model with a public repository, otherwise null.

The style to follow:

- No marketing words ("state-of-the-art", "revolutionary", "best-in-class") unless they are
  attributed to a benchmark result in the same sentence.
- No prices. Bud shows its own.
- Nothing about Bud, routes or hosting regions.
- Every list item is a single sentence of at most 300 characters.

By kind, cover what a user choosing a model needs:

- `chat`: reasoning or thinking modes, tool use, vision, coding, and the context window from `facts`.
- `embedding`: output dimensions, languages, input limit, and retrieval benchmarks such as MTEB.
- `image`: generation and editing, resolution, and text rendering.
- `stt`: languages, batch or streaming, diarization, domain tuning (medical, phone), and accuracy (WER).
- `tts`: languages, voices, voice cloning, emotion or style control, and latency.

## Output

Write `catalog/results/<slug>.json`, exactly in this shape:

```json
{
  "slug": "claude-sonnet-4-5",
  "canonical": "claude-sonnet-4-5",
  "status": "ok",
  "researched_on": "2026-09-24",
  "method": "claude-code-subagent",
  "maker": "Anthropic",
  "details": {
    "description": "...",
    "advantages": ["..."],
    "disadvantages": ["..."],
    "use_cases": ["..."],
    "evaluations": [{"name": "SWE-bench Verified", "score": 77.2, "source": "https://www.anthropic.com/news/claude-sonnet-4-5"}],
    "languages": [],
    "website_url": "https://...",
    "github_url": null
  },
  "sources": [
    {"url": "https://www.anthropic.com/news/claude-sonnet-4-5", "title": "Introducing Claude Sonnet 4.5", "kind": "maker"}
  ],
  "notes": "Anything uncertain, conflicts with the catalog facts, or ids you could not pin down."
}
```

- `sources[].kind` is `maker`, `host` or `third_party`.
- `status: "insufficient_sources"` with `details: null` when you cannot pin the model down, or
  cannot find a maker, host or credible third-party page about it. Say why in `notes`.
- The file must be valid JSON. Check your output with
  `python scripts/model_docs_workflow/enrich_catalog.py merge --dry-run`, which validates every
  result file.
