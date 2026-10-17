"""Regenerate the complete representative census rather than checking in large output.

Usage: python -m research.continuity_fifth_couplings.write_census [filename]
"""
from pathlib import Path
from sys import argv
from json import dumps
from .verify import classify

def main():
    dest = Path(argv[1] if len(argv) > 1 else "portable_classification.json")
    if dest.exists():
        raise FileExistsError(f"refusing to overwrite {dest}")
    result = classify()
    dest.write_text(dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"written {dest} ({dest.stat().st_size:,} bytes)")
if __name__ == "__main__":
    main()
