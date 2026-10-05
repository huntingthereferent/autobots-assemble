from __future__ import annotations

import argparse
import json

from .audit import write_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="artifacts/security_report.json")
    args = parser.parse_args()

    report = write_report(args.report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
