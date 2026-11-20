"""Export docs/examples notebooks to .py."""

from pathlib import Path


def main() -> None:
    """Convert example notebooks in a source checkout to Python scripts."""
    package_dir = Path(__file__).resolve().parent
    notebook_dir = package_dir.parents[1] / "docs" / "examples"
    notebooks = sorted(path for path in notebook_dir.glob("*.ipynb") if path.is_file())
    if not notebooks:
        message = (
            f"No .ipynb notebooks found in {notebook_dir}. "
            "From an Energia source checkout, run `python -m pip install -e '.[docs]'` "
            "and then `python -m energia.export`."
        )
        raise SystemExit(message)

    import nbformat
    from nbconvert import PythonExporter

    exporter = PythonExporter()
    out_dir = package_dir / "library" / "examples"
    out_dir.mkdir(exist_ok=True)

    for nb_file in notebooks:
        with nb_file.open(encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        body, _ = exporter.from_notebook_node(nb)
        out_path = out_dir / f"{nb_file.stem}.py"
        out_path.write_text(body, encoding="utf-8")
        print(f"Exported {nb_file} → {out_path}")


if __name__ == "__main__":
    main()
