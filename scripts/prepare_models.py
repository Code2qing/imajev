"""Prepare base model and adapter files for imajev server.

Checks whether base model and adapter exist locally, downloading them if missing,
and adjusts artifacts/model.json if host/container paths differ.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path
from huggingface_hub import snapshot_download


def prepare_base_model(model_size: str = "2b") -> None:
    bundle_path = Path("artifacts/model.json") if model_size == "2b" else Path(f"artifacts/model-qwen{model_size}.json")
    
    # 1. If bundle already exists and points to a valid directory, we are good
    if bundle_path.is_file():
        try:
            data = json.loads(bundle_path.read_text())
            target_path = Path(data.get("path", ""))
            if target_path.is_dir():
                print(f"[prepare_models] Base model ({model_size}) verified at: {target_path}")
                return
        except Exception as e:
            print(f"[prepare_models] Warning reading existing bundle: {e}")

    # 2. Check if HF cache contains the snapshot already
    hf_home = Path(os.environ.get("HF_HOME", ".cache/huggingface")).resolve()
    repo_name = "Qwen/Qwen3.5-2B" if model_size == "2b" else f"Qwen/Qwen3.5-{model_size.upper()}"
    hf_model_dir = hf_home / "hub" / f"models--{repo_name.replace('/', '--')}" / "snapshots"
    
    if hf_model_dir.is_dir():
        snapshots = [p for p in hf_model_dir.iterdir() if p.is_dir()]
        if snapshots:
            valid_snapshot = str(snapshots[0])
            print(f"[prepare_models] Found cached base model snapshot at: {valid_snapshot}")
            bundle_path.parent.mkdir(parents=True, exist_ok=True)
            bundle_data = {
                "repo": repo_name,
                "revision": snapshots[0].name,
                "path": valid_snapshot,
            }
            bundle_path.write_text(json.dumps(bundle_data, indent=2) + "\n")
            print(f"[prepare_models] Updated {bundle_path} successfully.")
            return

    # 3. Otherwise run download_model.py
    print(f"[prepare_models] Downloading base model ({model_size}) via scripts/download_model.py...")
    cmd = [sys.executable, "scripts/download_model.py"]
    if model_size != "2b":
        cmd.extend(["--model", model_size])
    subprocess.run(cmd, check=True)


def prepare_adapter(repo: str = "mohit67890/imajev-2b", local_dir: str = "adapters/imajev-2b") -> None:
    adapter_path = Path(local_dir)
    # Check if key adapter files exist
    weights_safetensors = adapter_path / "adapter_model.safetensors"
    calibration_file = adapter_path / "calibration.json"

    if weights_safetensors.is_file() and calibration_file.is_file():
        print(f"[prepare_models] Adapter verified at: {adapter_path}")
        return

    print(f"[prepare_models] Adapter not found at {adapter_path}. Downloading {repo}...")
    adapter_path.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=repo,
        local_dir=str(adapter_path),
        ignore_patterns=["*.md", ".gitattributes"]
    )
    print(f"[prepare_models] Adapter downloaded to {adapter_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ensure models are present before starting server")
    parser.add_argument("--model-size", default=os.getenv("MODEL_SIZE", "2b"), help="Base model size (default: 2b)")
    parser.add_argument("--adapter-repo", default=os.getenv("HF_ADAPTER_REPO", "mohit67890/imajev-2b"), help="Adapter HF repo id")
    parser.add_argument("--adapter-dir", default=os.getenv("ADAPTER_DIR", "adapters/imajev-2b"), help="Adapter target directory")
    args = parser.parse_args()

    prepare_base_model(args.model_size)
    prepare_adapter(args.adapter_repo, args.adapter_dir)


if __name__ == "__main__":
    main()
