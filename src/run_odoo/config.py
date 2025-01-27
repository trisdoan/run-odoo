# FIXME: enhance to make it different
from pathlib import Path
from typing import Sequence, TypedDict, cast
from tomlkit.toml_file import TOMLFile
from tomlkit.toml_document import TOMLDocument
from tomlkit.exceptions import TOMLKitError
from platformdirs import user_config_path

# TODO: support pyproject?
FILENAMES = [".run_odoo.toml", "run_odoo.toml"]


# FIXME: check attr
class Profile(TypedDict, total=False):
    addons: str
    python_version: str


# FIXME: check attr
class Config(TypedDict, total=False):
    profile: Profile


class ConfigFile:

    def __init__(self, path: Path) -> None:
        self.path = path
        self.toml_file = TOMLFile(path)
        try:
            self.toml_doc = self.toml_file.read()
            self.configs: Config = cast(Config, self.toml_doc.unwrap())
        except OSError:  # TODO: for what?
            self.toml_doc = TOMLDocument()
        except TOMLKitError as e:
            # FIXME: implement exception
            raise

    def update(self, config: Config) -> None:
        pass

    def write(self) -> None:
        """
        Write in-memory config file at self.path
        """
        pass


def get_config_for_profile(
    config_path: Path | None, profile_name: str | None
) -> Profile:
    config = load_config(config_path)

    profile: Profile = {}
    if profile_name != config.get("profile", False):
        # FIXME: implement profile not exist in discovered file
        pass
    else:
        profile = config["profile"][profile_name]
    return profile


def load_config(config_path: Path | None) -> Config:
    config = _find_config_file(config_path)
    _sanity_check(config)
    return config


def _find_config_file(config_path: Path | None) -> Config:
    config: Config = {}
    found_file = None
    if config_path is not None and config_path.exists():
        found_file = config_path
    elif config_path is not None:
        # FIXME: implement not exist path
        pass
    if found_file is None:
        for search in [_search_config, _search_cwd]:
            found_file = search()
        # FIXME: what if it's still None

    if found_file is not None:
        config_file = ConfigFile(found_file)
        config.update(config_file.configs)
    return config


def _search_cwd() -> Path | None:
    """Find config file in current working directory"""
    directory = Path.cwd()
    for f in FILENAMES:
        if (directory / f).exists():
            return directory / f


def _search_config() -> Path | None:
    """Find config file in user’s default config directory, in the run_odoo subdirectory"""
    directory = user_config_path(appname="run_odoo", appauthor=False)
    for f in FILENAMES:
        if (directory / f).exists():
            return directory / f


def _sanity_check(config: Config) -> None:
    return
