#!/usr/bin/env python3
"""Publish an article to the main branch (Zenn deploy target), or clean it up.

Workflow model:
  * Zenn deploys from the `main` branch.
  * The repository holds ONLY the article that is currently being added.
  * Once an article is confirmed live on Zenn, remove it from the repo with
    `--cleanup`. Removing the file does NOT unpublish it on Zenn; the article
    stays live. This keeps main clean so each push only ever syncs the
    in-flight article and never re-syncs unrelated published articles.

Usage:
  python scripts/publish.py --slug <slug>              # publish to main
  python scripts/publish.py --slug <slug> --no-push    # commit only
  python scripts/publish.py --slug <slug> --cleanup    # remove after it is live
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import shutil
from lib.state import get_work_dir, load_checkpoint, save_checkpoint, list_work_slugs
from lib.zenn import get_translated_path, get_article_path, get_images_dir
from lib.git import (checkout_branch, get_current_branch, run_git,
                     add_files, commit, push, has_changes)

DEPLOY_BRANCH = "main"


def resolve_slug(arg_slug):
    if arg_slug:
        return arg_slug
    slugs = list_work_slugs()
    if not slugs:
        print("❌ No work directories found")
        sys.exit(1)
    return slugs[-1]


def cleanup(slug):
    """Remove a published article and its images from main (kept live on Zenn)."""
    article_path = get_article_path(slug)
    images_dst = get_images_dir(slug)

    checkout_branch(DEPLOY_BRANCH)
    run_git("pull", "--ff-only", "origin", DEPLOY_BRANCH)

    removed = False
    if article_path.exists():
        run_git("rm", str(article_path))
        removed = True
    if images_dst.exists():
        run_git("rm", "-r", str(images_dst))
        removed = True

    if not removed:
        print(f"ℹ️  Nothing to clean up for {slug}")
        return

    commit(f"Remove published article from repo: {slug} (kept live on Zenn)")
    push(DEPLOY_BRANCH)
    print(f"✓ Removed {slug} from {DEPLOY_BRANCH} and pushed (article stays live on Zenn)")

    checkpoint = load_checkpoint(slug)
    checkpoint["status"] = "cleaned"
    save_checkpoint(slug, checkpoint)


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
        print(f"→ After it is live, run: python scripts/publish.py --slug {slug} --cleanup")

    checkpoint["status"] = "pushed"
    checkpoint["article_path"] = str(article_path)
    save_checkpoint(slug, checkpoint)


def main():
    parser = argparse.ArgumentParser(description="Publish article to main (Zenn deploy branch)")
    parser.add_argument("--slug", help="Article slug (default: latest)")
    parser.add_argument("--no-push", action="store_true", help="Commit only, don't push")
    parser.add_argument("--cleanup", action="store_true",
                        help="Remove the article from the repo after it is live on Zenn")
    args = parser.parse_args()

    slug = resolve_slug(args.slug)

    if args.cleanup:
        cleanup(slug)
    else:
        publish(slug, args.no_push)


if __name__ == "__main__":
    main()
