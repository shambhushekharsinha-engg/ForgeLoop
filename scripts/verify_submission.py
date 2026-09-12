import sys
from pathlib import Path


def main():
    source_dir = Path("submissions/latest")
    print("=== ForgeLoop Pre-Flight Checklist ===")
    if not source_dir.exists():
        print(f"[FAIL] Error: Submission directory '{source_dir}' does not exist.")
        print("   Make sure you save your game artifacts there before packaging.")
        sys.exit(1)

    print(f"Found submission directory: {source_dir}")

    expected_files = [
        "machine_raw.bsg",
        "machine_tuned.bsg",
        "trajectory.csv",
        "build_history.json",
        "build_history_full.json",
        "chat_transcript.md",
    ]

    missing = False
    for file in expected_files:
        if (source_dir / file).exists():
            print(f"[OK] Found {file}")
        else:
            print(f"[FAIL] Missing {file}")
            missing = True

    if missing:
        print("\n[FAIL] Cannot package submission. Please add the missing artifacts.")
        sys.exit(1)

    print("\n[OK] All required artifacts present.")
    print("Run 'make package' to securely zip your submission!")


if __name__ == "__main__":
    main()
