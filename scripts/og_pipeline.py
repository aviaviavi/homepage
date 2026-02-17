#!/usr/bin/env python3
import argparse
import html
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
OG_DIR = ROOT / "images" / "og"
SITE_URL = "https://avi.press"


def slug_from_path(path: Path) -> str:
    return path.stem


def title_from_org(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lower().startswith("#+title:"):
            return line.split(":", 1)[1].strip()
    return path.stem


def run_magick(title: str, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    title = title.replace("\n", " ").strip()
    cmd = [
        "magick", "-size", "1200x630", "gradient:#0f172a-#1e293b",
        "-fill", "#38bdf8", "-draw", "rectangle 0,0 1200,14",
        "-fill", "white", "-font", "Helvetica-Bold", "-pointsize", "64",
        "-gravity", "northwest", "-annotate", "+70+70", "avi.press",
        "-font", "Helvetica", "-pointsize", "58", "-gravity", "center",
        "-fill", "white", "-interline-spacing", "10", "-annotate", "+0+20", title,
        "-font", "Helvetica", "-pointsize", "34", "-gravity", "southwest",
        "-annotate", "+70+50", "Avi Press",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)


def build_meta_block(title: str, canonical_url: str, image_url: str, is_home=False) -> str:
    desc = "Personal site and writing by Avi Press"
    if not is_home:
        desc = f"{title} — Avi Press"
    lines = [
        f'<link rel="canonical" href="{canonical_url}" />',
        f'<meta property="og:site_name" content="Avi Press" />',
        f'<meta property="og:type" content="{"website" if is_home else "article"}" />',
        f'<meta property="og:title" content="{html.escape(title, quote=True)}" />',
        f'<meta property="og:description" content="{html.escape(desc, quote=True)}" />',
        f'<meta property="og:url" content="{canonical_url}" />',
        f'<meta property="og:image" content="{image_url}" />',
        f'<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{html.escape(title, quote=True)}" />',
        f'<meta name="twitter:description" content="{html.escape(desc, quote=True)}" />',
        f'<meta name="twitter:image" content="{image_url}" />',
    ]
    return "\n".join(lines)


def strip_existing_meta(content: str) -> str:
    patterns = [
        r'\n?<link rel="canonical" href="[^"]*"\s*/?>',
        r'\n?<meta property="og:[^"]+" content="[^"]*"\s*/?>',
        r'\n?<meta name="twitter:[^"]+" content="[^"]*"\s*/?>',
    ]
    for p in patterns:
        content = re.sub(p, "", content)
    return content


def inject_into_html(path: Path, block: str):
    content = path.read_text(encoding="utf-8")
    content = strip_existing_meta(content)
    content = content.replace("</head>", block + "\n</head>")
    path.write_text(content, encoding="utf-8")


def update_org_head(path: Path, block: str):
    lines = path.read_text(encoding="utf-8").splitlines()
    filtered = [ln for ln in lines if not (ln.startswith("#+HTML_HEAD_EXTRA: <meta property=\"og:") or ln.startswith("#+HTML_HEAD_EXTRA: <meta name=\"twitter:") or ln.startswith("#+HTML_HEAD_EXTRA: <link rel=\"canonical\""))]
    head_lines = [f"#+HTML_HEAD_EXTRA: {ln}" for ln in block.splitlines()]
    insert_idx = 0
    for i, ln in enumerate(filtered):
        if ln.startswith("#+HTML_HEAD_EXTRA:"):
            insert_idx = i + 1
    new_lines = filtered[:insert_idx] + head_lines + filtered[insert_idx:]
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def run_all():
    org_posts = sorted(POSTS_DIR.glob("*.org"))
    run_magick("Avi Press", OG_DIR / "site.png")

    # homepage metadata
    home_block = build_meta_block("Avi Press", f"{SITE_URL}/", f"{SITE_URL}/images/og/site.png", is_home=True)
    inject_into_html(ROOT / "index.html", home_block)
    update_org_head(ROOT / "index.org", home_block)

    # per-post metadata + images
    html_posts = {p.stem: p for p in POSTS_DIR.glob("*.html")}
    for org_path in org_posts:
        slug = slug_from_path(org_path)
        title = title_from_org(org_path)
        image_rel = f"images/og/{slug}.png"
        image_abs = f"{SITE_URL}/{image_rel}"
        canonical = f"{SITE_URL}/posts/{slug}.html"
        run_magick(title, ROOT / image_rel)
        block = build_meta_block(title, canonical, image_abs)
        update_org_head(org_path, block)
        html_path = html_posts.get(slug)
        if html_path:
            inject_into_html(html_path, block)


def main():
    parser = argparse.ArgumentParser(description="Generate OG images and inject OG/Twitter metadata")
    parser.add_argument("command", choices=["run"], nargs="?", default="run")
    args = parser.parse_args()
    if args.command == "run":
        run_all()


if __name__ == "__main__":
    main()
