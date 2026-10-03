---
name: youtube-info
description: Extract information from a YouTube video (title, channel, date, duration, views, description, chapters, tags, and transcript/subtitles) from its URL or ID. Use whenever the user shares a youtube.com / youtu.be link or asks to summarize, analyze, quote or get the transcript of a YouTube video.
---

# youtube-info

Fetches YouTube metadata and transcript with `yt-dlp` and `youtube-transcript-api`.

## Usage

```bash
python3 <skill-dir>/scripts/youtube_info.py "<url-or-id>" [--lang es,en] [--no-transcript] [--format json|md] [--out FILE]
```

- The script installs missing dependencies (`yt-dlp`, `youtube-transcript-api`) with pip on first run, so it works in Claude Code, Cowork and other sandboxes.
- Output (default `md`) has metadata, chapters, description and the transcript with timestamps. Use `--format json` for structured data.
- After running it, summarize or answer from the output. For long transcripts, write to `--out` and read in parts.

## Network requirements

The sandbox must be able to reach `youtube.com`, `*.googlevideo.com` and `i.ytimg.com`. If the script reports `403`/`EGRESS_BLOCKED`/proxy errors, the environment's network policy blocks YouTube: tell the user to allow those domains in the environment's network settings (Cowork/Claude Code on the web: Settings → network access → add `youtube.com`). Do not try to bypass the proxy.

If YouTube blocks the request as bot traffic (cloud IPs often are), retry with `--cookies cookies.txt` (exported browser cookies) or ask the user to paste the transcript.
