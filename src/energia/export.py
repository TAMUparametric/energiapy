"""Export docs/examples notebooks to .py"""


def main():
    from pathlib import Path

    import nbformat
    from nbconvert import PythonExporter

    # Example: export all notebooks from docs/examples
    nb_dir = Path(__file__).parent.parent.parent / "docs" / "examples"
    print(Path(__file__).parent)
    out_dir = Path(__file__).parent / "library" / "examples"
    out_dir.mkdir(exist_ok=True)

    for nb_file in nb_dir.glob("*.ipynb"):
        with open(nb_file, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        exporter = PythonExporter()
        body, _ = exporter.from_notebook_node(nb)
        out_path = out_dir / f"{nb_file.stem}.py"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"Exported {nb_file} → {out_path}")


if __name__ == "__main__":
    main()
