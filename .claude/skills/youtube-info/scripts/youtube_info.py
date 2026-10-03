#!/usr/bin/env python3
"""Extract metadata and transcript from a YouTube video."""
import argparse
import importlib
import json
import re
import subprocess
import sys


def ensure(mod, pkg):
    try:
        return importlib.import_module(mod)
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", pkg],
            stdout=sys.stderr,
        )
        return importlib.import_module(mod)


def video_id(s):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})", s)
    if m:
        return m.group(1)
    if re.fullmatch(r"[\w-]{11}", s):
        return s
    sys.exit(f"Cannot parse a YouTube video ID from: {s}")


def fmt_time(t):
    t = int(t)
    return f"{t // 3600:d}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60:d}:{t % 60:02d}"


def get_meta(vid, cookies):
    yt_dlp = ensure("yt_dlp", "yt-dlp")
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    if cookies:
        opts["cookiefile"] = cookies
    with yt_dlp.YoutubeDL(opts) as ydl:
        d = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
    keys = ["title", "channel", "uploader", "channel_url", "upload_date", "duration", "view_count",
            "like_count", "comment_count", "categories", "tags", "description", "chapters", "language"]
    meta = {k: d.get(k) for k in keys}
    meta["url"] = f"https://www.youtube.com/watch?v={vid}"
    return meta


def get_transcript(vid, langs):
    mod = ensure("youtube_transcript_api", "youtube-transcript-api")
    api = mod.YouTubeTranscriptApi()
    tr = api.fetch(vid, languages=langs)
    return [{"start": s.start, "text": s.text} for s in tr]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--lang", default="es,en")
    ap.add_argument("--no-transcript", action="store_true")
    ap.add_argument("--format", choices=["json", "md"], default="md")
    ap.add_argument("--cookies")
    ap.add_argument("--out")
    a = ap.parse_args()
    vid = video_id(a.video)

    result = {"id": vid}
    try:
        result["meta"] = get_meta(vid, a.cookies)
    except Exception as e:
        result["meta_error"] = str(e)
    if not a.no_transcript:
        try:
            result["transcript"] = get_transcript(vid, a.lang.split(","))
        except Exception as e:
            result["transcript_error"] = str(e)

    if a.format == "json":
        out = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        m = result.get("meta") or {}
        L = [f"# {m.get('title', vid)}", ""]
        for label, k in [("Channel", "channel"), ("URL", "url"), ("Date", "upload_date"),
                         ("Views", "view_count"), ("Likes", "like_count"), ("Tags", "tags")]:
            if m.get(k) is not None:
                L.append(f"- **{label}:** {m[k]}")
        if m.get("duration"):
            L.append(f"- **Duration:** {fmt_time(m['duration'])}")
        if m.get("chapters"):
            L += ["", "## Chapters"] + [f"- {fmt_time(c['start_time'])} {c['title']}" for c in m["chapters"]]
        if m.get("description"):
            L += ["", "## Description", m["description"]]
        if result.get("transcript"):
            L += ["", "## Transcript"] + [f"[{fmt_time(s['start'])}] {s['text']}" for s in result["transcript"]]
        for k in ("meta_error", "transcript_error"):
            if result.get(k):
                L += ["", f"**{k}:** {result[k]}"]
        out = "\n".join(L)

    if a.out:
        open(a.out, "w", encoding="utf-8").write(out)
        print(f"Wrote {a.out}")
    else:
        print(out)
    if "meta_error" in result and "transcript" not in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
