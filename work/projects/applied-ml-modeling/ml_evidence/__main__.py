from __future__ import annotations

import argparse
import json

from .modeling import train_and_evaluate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()

    result = train_and_evaluate(args.output_dir)
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
