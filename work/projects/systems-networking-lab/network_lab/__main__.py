from __future__ import annotations

import argparse
import json

from .measure import write_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="artifacts/network_report.json")
    args = parser.parse_args()
    print(json.dumps(write_report(args.report), indent=2))


if __name__ == "__main__":
    main()
