"""Execute case-study notebooks in fresh kernels without changing source files."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main() -> None:
    """Write executed copies to a separate directory and fail on cell errors."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / "docs/examples/case_studies"
    output = args.output.resolve()
    if output == source:
        parser.error("Choose an output directory outside the source notebooks.")
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.glob("*.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(
            notebook,
            timeout=600,
            kernel_name="python3",
            resources={"metadata": {"path": str(output)}},
        ).execute()
        nbformat.write(notebook, output / path.name)
        print(f"Passed: {path.name}", flush=True)


if __name__ == "__main__":
    main()
