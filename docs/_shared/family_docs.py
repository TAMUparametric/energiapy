"""Common documentation configuration; package-specific content stays local."""

import os
import tomllib
from pathlib import Path

FAMILY = (
    ("gana", "Gana", "Mathematical programming", "gana"),
    ("energia", "Energia", "Energy systems", "energiapy"),
    ("vaelchi", "Vaelchi", "Time-series reduction", "vaelchi"),
)


def configure(config, docs, *, incompatible=()):
    """Apply the vendored baseline and explicit development cross-links.

    Release inventories must be selected after verifying compatible hosted
    versions. Discovery links do not imply runtime dependencies.
    """
    shared = Path(__file__).resolve().parent
    metadata = tomllib.loads((docs.parent / "pyproject.toml").read_text())
    config["release"] = metadata["project"]["version"]
    config["version"] = config["release"]
    config["html_theme"] = "sphinx_book_theme"
    config["nb_execution_mode"] = "off"
    config["html_context"] = {"default_mode": "auto"}
    config["html_copy_source"] = True
    config["html_last_updated_fmt"] = ""
    config["templates_path"] = [str(shared / "templates"), "_templates"]
    config["html_static_path"] = ["_static", str(shared / "static")]
    config["html_css_files"] = ["custom.css", "family.css"]
    config["html_sidebars"] = {
        "**": ["navbar-logo.html", "icon-links.html", "search-button-field.html",
               "family-nav.html", "sbt-sidebar-nav.html"]
    }
    config["exclude_patterns"] = list(dict.fromkeys([
        *config.get("exclude_patterns", []), "_shared", "_build",
        "jupyter_execute", "**/.ipynb_checkpoints",
    ]))
    if "sphinx.ext.intersphinx" not in config["extensions"]:
        config["extensions"].append("sphinx.ext.intersphinx")
    config["intersphinx_disabled_reftypes"] = ["*"]
    config["intersphinx_mapping"] = {}
    development = (
        os.environ.get("READTHEDOCS_VERSION_TYPE", "branch") != "tag"
        and os.environ.get("READTHEDOCS_VERSION") != "stable"
    )
    links = []
    for key, title, purpose, domain in FAMILY:
        url = f"https://{domain}.readthedocs.io/en/latest/"
        current = title == config["project"]
        links.append({"name": title, "purpose": purpose, "url": url,
                      "current": current})
        if development and not current and key not in incompatible:
            config["intersphinx_mapping"][key] = (
                url, str(shared / "inventories" / f"{key}.inv")
            )
    config["html_context"]["family_links"] = links
    # RTD records the actual Git ref even when its display version is an alias.
    git_ref = os.environ.get("READTHEDOCS_GIT_IDENTIFIER")
    if git_ref:
        config["html_theme_options"]["repository_branch"] = git_ref
