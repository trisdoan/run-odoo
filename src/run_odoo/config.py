# FIXME: enhance to make it different - add validation and better error handling
from pathlib import Path
from typing import Sequence, TypedDict, cast
from tomlkit.toml_file import TOMLFile
from tomlkit.toml_document import TOMLDocument
from tomlkit.exceptions import TOMLKitError
from platformdirs import user_config_path

# TODO: support pyproject?
FILENAMES = [".run_odoo.toml", "run_odoo.toml"]


class Profile(TypedDict, total=False):
    addons: list[str]
    version: float
    python_version: str
    enterprise: bool
    themes: bool
    db: str
    path: str
    extra_params: str
    http_port: int
    log_level: str
    workers: int
    db_host: str
    db_user: str
    db_password: str


class Config(TypedDict, total=False):
    profile: dict[str, Profile]


class ConfigFile:

    def __init__(self, path: Path) -> None:
        self.path = path
        self.toml_file = TOMLFile(path)
        try:
            self.toml_doc = self.toml_file.read()
            self.configs: Config = cast(Config, self.toml_doc.unwrap())
        except OSError:  # TODO: for what? - handle file not found or permission errors
            self.toml_doc = TOMLDocument()
            self.configs = {}
        except TOMLKitError as e:
            # FIXME: implement exception - create custom config exceptions
            raise ValueError(f"Invalid TOML configuration: {e}")

    def update(self, config: Config) -> None:
        """Update configuration in memory"""
        # FIXME: implement configuration updates
        self.configs.update(config)
        for key, value in config.items():
            self.toml_doc[key] = value

    def write(self) -> None:
        """
        Write in-memory config file at self.path
        """
        # FIXME: implement configuration writing
        self.toml_file.write(self.toml_doc)


def get_config_for_profile(
    config_path: Path | None, profile_name: str | None
) -> Profile:
    """Get configuration for a specific profile"""
    config = load_config(config_path)

    profile: Profile = {}
    if profile_name and "profile" in config:
        if profile_name not in config["profile"]:
            # FIXME: implement profile not exist in discovered file - raise ProfileNotFoundError
            raise ValueError(f"Profile '{profile_name}' not found in configuration")
        profile = config["profile"][profile_name]
    else:
        # FIXME: handle case when no profile specified
        if "profile" in config and config["profile"]:
            # Use first profile as default
            first_profile = next(iter(config["profile"].values()))
            profile = first_profile

    return profile


def load_config(config_path: Path | None) -> Config:
    """Load configuration from file"""
    config = _find_config_file(config_path)
    _sanity_check(config)
    return config


def _find_config_file(config_path: Path | None) -> Config:
    """Find and load configuration file"""
    config: Config = {}
    found_file = None

    if config_path is not None and config_path.exists():
        found_file = config_path
    elif config_path is not None:
        # FIXME: implement not exist path - raise FileNotFoundError with helpful message
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    if found_file is None:
        for search in [_search_config, _search_cwd]:
            found_file = search()
            if found_file:
                break
        # FIXME: what if it's still None - create default config or raise error

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
    return None


def _search_config() -> Path | None:
    """Find config file in user’s default config directory, in the run_odoo subdirectory"""
    directory = user_config_path(appname="run_odoo", appauthor=False)
    for f in FILENAMES:
        if (directory / f).exists():
            return directory / f
    return None


def _sanity_check(config: Config) -> None:
    """Validate configuration structure and values"""
    # FIXME: implement configuration validation
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")

    if "profile" in config:
        if not isinstance(config["profile"], dict):
            raise ValueError("Profiles must be a dictionary")

        for profile_name, profile_config in config["profile"].items():
            if not isinstance(profile_config, dict):
                raise ValueError(f"Profile '{profile_name}' must be a dictionary")

            # Validate version if present
            if "version" in profile_config:
                version = profile_config["version"]
                if not isinstance(version, (int, float)):
                    raise ValueError(
                        f"Version in profile '{profile_name}' must be a number"
                    )

    return
