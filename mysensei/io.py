import mysensei
import os
import tomllib
from jinja2 import Template, Environment, FileSystemLoader

def get_lib_path() -> str:
    """Path to current library"""
    return os.path.join(
        os.path.dirname(mysensei.__file__),
        "..",
    )


def get_config_path() -> str:
    """Path to conf folder"""
    return os.path.join(
        get_lib_path(),
        "config",
    )


def get_conf_toml(filename) -> dict:
    """Get conf/`filename` (toml files)"""
    filepath = os.path.join(get_config_path(), filename)
    with open(filepath, "rb") as f:
        conf = tomllib.load(f)
    return conf


def _get_template_dirpath() -> str:
    """Get path to template folder"""
    return os.path.join(
        get_lib_path(),
        "templates",
    )

_TEMPLATE_LOADER = FileSystemLoader(_get_template_dirpath())

def get_jinja_template(template_name: str, version: int) -> Template:
    """Get templates/`filename`"""
    template_environment = Environment(loader=_TEMPLATE_LOADER)
    filename = template_name + "/" + str(version) + ".jinja"  # /" is the path 
        # separator for jinja, even on Windows
    template = template_environment.get_template(filename)
    return template
