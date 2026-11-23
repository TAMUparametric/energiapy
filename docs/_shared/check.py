"""Verify a vendored docs snapshot, optionally against another checkout."""

import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--against", type=Path, help="Another docs/_shared directory")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "manifest.json").read_text())
    for name, expected in manifest["sha256"].items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"Shared docs baseline drift: {name}")
    if args.against:
        for name in ["manifest.json", *manifest["sha256"]]:
            if (root / name).read_bytes() != (args.against / name).read_bytes():
                raise SystemExit(f"Shared docs copies differ: {name}")
    print(f"Shared docs baseline {manifest['version']}: verified")


if __name__ == "__main__":
    main()
