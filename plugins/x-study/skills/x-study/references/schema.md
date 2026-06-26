# Canonical JSON + Enrichment + Thread + Manual-Paste Template

## Canonical JSON (from fetch_post.py / manual)
Fields: source_url, tweet_id, author_name, handle, posted_at, lang, text (HTML-unescaped),
expanded_urls, media[{type,url,local_path,width,height}], quote_post, thread_items[],
provider, raw_provider_ref, captured_at, truncated, tags[], provenance{…}.
NO title, NO media[].alt — those come from enrichment.json. `tags[]` in canonical JSON is
emitted as-is by fetch_post.py (empty list); Claude must NOT populate it — enrichment.json
`tags` is the authoritative source. `captured_at` is set by fetch_post.py to processing time
(UTC, `YYYY-MM-DDTHH:MM:SSZ`). `media[]` may include non-photo items (type `video`/`gif`)
which are preserved as links — only `type: photo` items are downloaded (`local_path` set);
non-photo items keep `local_path: null` and render as a link to the original.

## Single tweet vs. thread (the one contract that matters)
- **Single tweet → `thread_items == []`.** Renderers use the top-level `text`/`media`; **no**
  banner and **no** `provenance` block are injected. Output is unchanged from v0.1 (no regression).
- **Thread → `thread_items` is non-empty and AUTHORITATIVE.** Renderers iterate it and ignore
  top-level `media` for figures. Top-level `text`/`media`/`posted_at` **mirror the first item**
  so existing title/date/`dcterms:modified` logic keeps working unchanged.

### `thread_items[]` (chronological, 1 entry per tweet)
```json
{
  "index": 1,
  "text": "HTML-unescaped verbatim tweet text",
  "url": "https://x.com/<handle>/status/<id>",   // per-tweet permalink (citation)
  "posted_at": "Wed Jun 24 11:52:51 +0000 2026",  // original string, or null
  "posted_at_utc": "2026-06-24T11:52:51Z",          // ISO-8601 UTC, or null
  "media": [{"type":"photo","url":"https://pbs.twimg.com/…","local_path":null,"width":null,"height":null}]
}
```

### `provenance` block (present ONLY for threads; Dublin Core / Memento mapping)
```json
{
  "source_url": "https://x.com/<handle>/status/<first_id>",  // dcterms:source
  "captured_at": "2026-06-26T11:50:00Z",                       // dcterms:dateSubmitted (UTC)
  "capture_method": "manual paste, x-study v0.2",              // dcterms:provenance
  "thread_completeness": "3 of 3",                              // "N of M"; M = "unverified" if unknown
  "capture_scope": "Excludes: quoted tweets, video/GIF media, expanded-URL resolution, replies by other users."
}
```
`thread_completeness`: N = number of pasted tweets. M = N **only if the user confirms the thread
is complete**, otherwise `"<N> of unverified"`. Never guess M — the mirror exposes a `replies`
count but **no** sibling list, so the true thread length is not knowable from the API.

## Enrichment JSON (written by Claude)
```json
{ "title": "Author - Topic", "alt_texts": {"images/img1.jpg": "descriptive alt"}, "tags": ["macro"] }
```
`alt_texts` keys are `local_path` values — they are shared across the whole thread (one global
image counter `img1..imgN` spans all tweets), so a key maps to exactly one chart regardless of
which tweet owns it.

## Output (md + epub) — produced by build_md.py / build_epub.py, NOT hand-written
Both renderers consume the **same** canonical + enrichment JSON, so md and epub stay in lockstep
(parity) and are byte-deterministic. Do not hand-write the markdown; call `build_md.py` (see
SKILL.md step 4). The markdown front-matter carries title/url/author/handle/posted_at/processed_at/
type/tags; threads additionally render a completeness banner and per-tweet blocks.

## Manual-paste template (threads, or when fetch fails)
Ask the user to paste, in order, **in one turn**, the tweets separated by a line containing only
`---`. For each tweet capture verbatim text + any `pbs.twimg.com` image URLs (or local paths).
Also ask: author name + @handle, the thread's first-tweet date, and **"is this the complete
thread?"** (drives `thread_completeness`). Build the canonical JSON yourself (populate
`thread_items[]` + `provenance`), **echo the assembled JSON back for confirmation**, then continue
at step 2/3. A single pasted tweet uses `thread_items=[]` (single-tweet path).
