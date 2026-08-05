#!/usr/bin/env python3
"""Publish an article to the main branch (Zenn deploy target).

Publishing model (IMPORTANT):
  * Zenn deploys from the `main` branch.
  * Published articles and their images MUST stay in the repo permanently.
    Zenn DELETES the images of a live article if their files are removed from
    the deploy branch (removing a file is treated as a deletion on Zenn and
    purges the content-addressed image object). Never delete a published
    article or its images from `main`.
  * To add a new article, just publish it. Re-syncing unchanged existing
    articles is a no-op on Zenn, so keeping them in the repo is safe.

Usage:
  python scripts/publish.py --slug <slug>            # publish to main
  python scripts/publish.py --slug <slug> --no-push  # commit only
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import shutil
from lib.state import get_work_dir, load_checkpoint, save_checkpoint, list_work_slugs
from lib.zenn import get_translated_path, get_article_path, get_images_dir
from lib.git import checkout_branch, run_git, add_files, commit, push, has_changes

DEPLOY_BRANCH = "main"


def resolve_slug(arg_slug):
    if arg_slug:
        return arg_slug
    slugs = list_work_slugs()
    if not slugs:
        print("❌ No work directories found")
        sys.exit(1)
    return slugs[-1]


def publish(slug, no_push):
    translated = get_translated_path(slug)
    if not translated.exists():
        print(f"❌ {translated} not found")
        sys.exit(1)

    checkpoint = load_checkpoint(slug)
    title = checkpoint.get("title", slug)
    article_path = get_article_path(slug)
    images_src = get_work_dir(slug) / "images"
    images_dst = get_images_dir(slug)

    checkout_branch(DEPLOY_BRANCH)
    run_git("pull", "--ff-only", "origin", DEPLOY_BRANCH)

    # Copy article
    article_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(translated, article_path)
    print(f"✓ {article_path}")

    # Copy images
    if images_src.exists() and any(images_src.iterdir()):
        images_dst.mkdir(parents=True, exist_ok=True)
        for img in images_src.iterdir():
            shutil.copy(img, images_dst / img.name)
        print(f"✓ {len(list(images_src.iterdir()))} images → {images_dst}")

    add_files(str(article_path))
    if images_dst.exists():
        add_files(str(images_dst))

    if not has_changes():
        print("ℹ️  No changes")
        return

    commit(f"Add article: {title}")
    print(f"✓ Committed on {DEPLOY_BRANCH}")

    if not no_push:
        push(DEPLOY_BRANCH)
        print(f"✓ Pushed to origin/{DEPLOY_BRANCH} (Zenn will deploy shortly)")
        print(f"→ Verify: https://zenn.dev/opensearch/articles/{slug}")

    checkpoint["status"] = "pushed"
    checkpoint["article_path"] = str(article_path)
    save_checkpoint(slug, checkpoint)


def main():
    parser = argparse.ArgumentParser(description="Publish article to main (Zenn deploy branch)")
    parser.add_argument("--slug", help="Article slug (default: latest)")
    parser.add_argument("--no-push", action="store_true", help="Commit only, don't push")
    args = parser.parse_args()

    publish(resolve_slug(args.slug), args.no_push)


if __name__ == "__main__":
    main()
