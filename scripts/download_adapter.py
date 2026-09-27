"""Download an adapter checkpoint from Hugging Face Hub into local directory.

Usage:
    python scripts/download_adapter.py
    python scripts/download_adapter.py --repo mohit67890/imajev-2b --local-dir adapters/imajev-2b
"""
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download


def main() -> None:
    parser = argparse.ArgumentParser(description="Download an adapter from Hugging Face Hub")
    parser.add_argument("--repo", default="mohit67890/imajev-2b", help="Hugging Face repo id (default: mohit67890/imajev-2b)")
    parser.add_argument("--local-dir", default="adapters/imajev-2b", help="Local directory to store adapter files")
    args = parser.parse_args()

    local_path = Path(args.local_dir)
    print(f"Downloading adapter {args.repo} into {local_path}...", flush=True)
    snapshot_download(
        repo_id=args.repo,
        local_dir=str(local_path),
        ignore_patterns=["*.md", ".gitattributes"]
    )
    print(f"Adapter saved to {local_path}", flush=True)


if __name__ == "__main__":
    main()
