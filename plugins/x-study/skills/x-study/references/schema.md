# Canonical JSON + Enrichment + Manual-Paste Template

## Canonical JSON (from fetch_post.py / manual)
Fields: source_url, tweet_id, author_name, handle, posted_at, lang, text (HTML-unescaped),
expanded_urls, media[{type,url,local_path,width,height}], quote_post, thread_items[],
provider, raw_provider_ref, captured_at, truncated, tags[].
NO title, NO media[].alt — those come from enrichment.json. `tags[]` in canonical JSON is
emitted as-is by fetch_post.py (empty list); Claude must NOT populate it — enrichment.json
`tags` is the authoritative source. `thread_items` is an array so multi-post pastes work
without a schema change. `captured_at` is set by fetch_post.py to processing time
(UTC, `YYYY-MM-DDTHH:MM:SSZ`). `media[]` may include non-photo items (type `video`/`gif`)
which are preserved as links — only `type: photo` items are downloaded (`local_path` set);
non-photo items keep `local_path: null` and render as a link to the original.

## Enrichment JSON (written by Claude)
```json
{ "title": "Author - Topic", "alt_texts": {"images/img1.jpg": "descriptive alt"}, "tags": ["macro"] }
```

## Markdown output template
```
---
title: {enrichment.title}
url: {source_url}
author: {author_name}
handle: {handle}
posted_at: {posted_at}
processed_at: {captured_at}
type: x-post
tags: [{tags}]   # {tags} from enrichment.json — do NOT read from canonical JSON tags[]
---

# {author_name} (@{handle})
*Posted: {posted_at} · {provider}*

{faithful paragraphs}

![{enrichment.alt_texts[local_path]}](images/{file})

---
Source: {source_url} · captured {captured_at} · via {provider}
```

## Manual-paste template (fallback when fetch fails)
Ask the user for: author name + @handle; post date; full text (verbatim, blank line between
paragraphs); image URLs (pbs.twimg.com) or local file paths, in order. Build the canonical
JSON yourself and continue at step 2/3.
