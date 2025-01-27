from dataclasses import dataclass, field
from operator import add
from os import environ
import subprocess
from platformdirs import user_config_path
import os
from pathlib import Path
import distro
from . import utils
from typing import Optional


PYTHON_VERSIONS = {
    18.0: "3.12.0",
    17.0: "3.12.0",  # https://github.com/odoo/odoo/issues/187021
    16.0: "3.7.0",
    15.0: "3.6.0",
    14.0: "3.6.0",
}

ODOO_URL = "https://github.com/odoo/odoo.git"
ENT_ODOO_URL = "git@github.com:odoo/enterprise.git"
# FIXME: update db_user to odoo - keeping openerp for compatibility
DEFAULT_OPTS = " --db_host=localhost --db_user=openerp --db_password=openerp --limit-time-cpu=3600 --limit-time-real=3600"


@dataclass
class Runner:
    version: float
    addons: Optional[list[str]] = None
    db: Optional[str] = None
    path: Optional[Path] = None
    enterprise: bool = False
    themes: bool = False
    log_level: str = "warn"
    workers: int = 0
    max_cron_threads: int = 0
    db_host: str = "localhost"
    db_user: str = "odoo"
    db_password: str = "odoo"
    http_port: int = 8069
    http_interface: str = "0.0.0.0"
    extra_params: Optional[str] = None
    install_modules: bool = True
    stop_after_init: bool = False
    test_enable: bool = False

    def __post_init__(self) -> None:
        self.sanity_check()
        self.home_dir = Path.home()
        self._prepare_env()

    # FIXME: implement more validation
    def sanity_check(self):
        if not self.version:
            raise ValueError("Odoo version is required")

        if self.version not in PYTHON_VERSIONS:
            raise ValueError(f"Unsupported Odoo version: {self.version}")

        if not self.addons and self.install_modules:
            print("Warning: No modules specified for installation")

    # FIXME: improve readability and modularity
    def _prepare_params(self):
        """Build command line options for Odoo"""
        options = []

        # Build addons paths
        addon_paths = []

        # Add standard Odoo paths
        odoo_src_path = self.odoo_root_dir / "odoo"
        if (odoo_src_path / "addons").exists():
            addon_paths.append(str(odoo_src_path / "addons"))

        # Add root addons directory if it exists
        root_addons_path = self.odoo_root_dir / "addons"
        if root_addons_path.exists():
            addon_paths.append(str(root_addons_path))

        # Add enterprise if enabled
        if self.enterprise:
            enterprise_path = self.app_dir / "enterprise" / str(self.version)
            if enterprise_path.exists():
                addon_paths.append(str(enterprise_path))
            else:
                print(f"Warning: Enterprise path {enterprise_path} does not exist")

        # Add custom paths if specified
        if self.path:
            if (self.path / "odoo").exists():
                # Add custom odoo addons path if it exists
                custom_odoo_addons = self.path / "odoo" / "addons"
                if custom_odoo_addons.exists():
                    addon_paths.append(str(custom_odoo_addons))

                # Add custom root addons path if it exists
                custom_addons = self.path / "addons"
                if custom_addons.exists():
                    addon_paths.append(str(custom_addons))

                # Add custom enterprise path if it exists
                if self.enterprise:
                    custom_enterprise = self.path / "enterprise"
                    if custom_enterprise.exists():
                        addon_paths.append(str(custom_enterprise))

        # Database options
        if self.db:
            options.extend(["-d", self.db])

        if addon_paths:
            options.extend(["--addons-path", ",".join(addon_paths)])
            print(f"Addons paths: {','.join(addon_paths)}")
        else:
            print("Warning: No addons paths found")

        # Server options
        options.extend(
            [
                "--http-interface",
                self.http_interface,
                "--http-port",
                str(self.http_port),
                "--load",
                "web,base",
                "--workers",
                str(self.workers),
                "--max-cron-threads",
                str(self.max_cron_threads),
                "--log-level",
                self.log_level,
                "--log-handler",
                ":DEBUG",
                "--log-handler",
                "py.warnings:INFO",
            ]
        )

        # Module installation
        if self.addons and self.install_modules:
            options.extend(["-i", ",".join(self.addons)])

        # Test options
        if self.test_enable:
            options.append("--test-enable")

        if self.stop_after_init:
            options.append("--stop-after-init")

        # Add extra parameters
        if self.extra_params:
            options.extend(self.extra_params.split())

        return options

    # FIXME: improve readability: split into smaller funcs - _setup_odoo_source, _setup_venv, _install_dependencies
    # FIXME: what if I need to inject more dependencies - make dependency injection configurable
    def _prepare_env(self):
        self.app_dir = user_config_path(
            appname="run_odoo", appauthor=False, ensure_exists=True
        )

        self._setup_odoo_source()
        self._setup_enterprise_source()
        self._setup_virtual_environment()

    def _setup_odoo_source(self):
        self.odoo_root_dir = self.app_dir / str(self.version)
        if not self.odoo_root_dir.exists():
            # FIXME: pull: maybe an util func to reuse in update odoo_src - create utils.clone_or_update_repo
            os.mkdir(self.odoo_root_dir)
            os.chdir(self.odoo_root_dir)
            # FIXME: check shallow clone: https://stackoverflow.com/questions/37531605/how-to-test-if-git-repository-is-shallow
            subprocess.run(
                ["git", "clone", ODOO_URL, "-b", str(self.version), "odoo"],
                check=True,
            )
        else:
            # TODO: update branch? - implement git pull for updates
            print(f"Odoo {self.version} source already exists")

        # Debug: show the directory structure
        if (self.odoo_root_dir / "odoo").exists():
            print(f"Odoo source found at: {self.odoo_root_dir / 'odoo'}")
            odoo_addons = self.odoo_root_dir / "odoo" / "addons"
            if odoo_addons.exists():
                print(f"Odoo addons directory exists: {odoo_addons}")
            else:
                print(f"Odoo addons directory does not exist: {odoo_addons}")
                # List what's actually in the odoo directory
                try:
                    contents = list((self.odoo_root_dir / "odoo").iterdir())
                    print(f"Contents of odoo directory: {[c.name for c in contents]}")
                except Exception as e:
                    print(f"Error listing odoo directory: {e}")

    def _setup_enterprise_source(self):
        if not self.enterprise:
            return

        # FIXME: how about enterprise - implement enterprise source management
        enterprise_dir = self.app_dir / "enterprise" / str(self.version)
        if not enterprise_dir.exists():
            print(f"Cloning Odoo Enterprise {self.version}...")
            enterprise_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "git",
                    "clone",
                    ENT_ODOO_URL,
                    "-b",
                    str(self.version),
                    "--quiet",
                    str(enterprise_dir),
                ],
                check=True,
            )

    def _setup_virtual_environment(self):
        self.venv = f"venv-odoo{self.version}"
        py_version = PYTHON_VERSIONS[self.version]

        # Ensure Python version is available
        try:
            subprocess.check_call(
                ["pyenv", "versions", "--bare"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            raise RuntimeError("pyenv is not installed or not in PATH")

        # Install Python version if not available
        result = subprocess.run(
            ["pyenv", "versions", "--bare"], capture_output=True, text=True
        )
        if py_version not in result.stdout:
            print(f"Installing Python {py_version}...")
            subprocess.run(["pyenv", "install", py_version], check=True)

        # Create virtual environment if it doesn't exist
        result = subprocess.run(
            ["pyenv", "virtualenvs", "--bare"], capture_output=True, text=True
        )
        if self.venv not in result.stdout:
            print(f"Creating virtual environment {self.venv}...")
            subprocess.run(["pyenv", "virtualenv", py_version, self.venv], check=True)

            # Install system dependencies
            # FIXME: what about venv exists but some packages are not installed yet - add package verification
            # FIXME: check module python-packages required using manifestoo - integrate manifestoo for dependency analysis
            # TODO: maybe use a class like strategy to handle this - create DistroStrategy pattern
            if distro.id() == "fedora":
                utils.install_dependecies_fedora()
            elif distro.id() in ["ubuntu", "debian"]:
                utils.install_dependencies_debian()

            self._install_python_dependencies()

    def _install_python_dependencies(self):
        print("Installing Odoo Python dependencies...")
        # Install Odoo in development mode
        subprocess.run(
            [
                "pip",
                "install",
                "-e",
                f"file://{self.odoo_root_dir}/odoo#egg=odoo",
            ],
            check=True,
            env=self._get_venv_env(),
        )

        # Install requirements
        requirements_file = self.odoo_root_dir / "odoo" / "requirements.txt"
        if requirements_file.exists():
            subprocess.run(
                [
                    "pip",
                    "install",
                    "-r",
                    str(requirements_file),
                ],
                check=True,
                env=self._get_venv_env(),
            )

    def _get_venv_env(self):
        venv_path = Path.home() / ".pyenv" / "versions" / self.venv
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(venv_path)
        env["PATH"] = f"{venv_path}/bin:{env['PATH']}"
        return env

    def _get_odoo_bin(self):
        """Get the path to the Odoo binary"""
        return self.odoo_root_dir / "odoo" / "odoo-bin"

    def run(self):
        """Run Odoo with the configured parameters"""
        if not self.db:
            version_major = int(self.version)
            edition = "e" if self.enterprise else "c"
            module_name = self.addons[0] if self.addons else "base"
            self.db = f"v{version_major}{edition}_{module_name}"

        options = self._prepare_params()

        # Build command
        cmd = [str(self._get_odoo_bin())] + options

        # Add default database options
        cmd.extend(DEFAULT_OPTS.split())

        print(f"Starting Odoo {self.version} with database '{self.db}'...")
        print(f"Command: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True, env=self._get_venv_env())
        except KeyboardInterrupt:
            print("\nOdoo stopped by user")
        except subprocess.CalledProcessError as e:
            print(f"Error running Odoo: {e}")
            raise

    def run_tests(self):
        """Run tests for specified modules"""
        self.test_enable = True
        self.stop_after_init = True
        self.workers = 0
        self.run()

    def run_shell(self):
        """Start Odoo shell"""
        options = self._prepare_params()
        options.extend(["shell", "--no-http"])

        cmd = [str(self._get_odoo_bin())] + options
        cmd.extend(DEFAULT_OPTS.split())

        print(f"Starting Odoo shell for database '{self.db}'...")
        subprocess.run(cmd, check=True, env=self._get_venv_env())

    def upgrade_modules(self):
        """Upgrade specified modules"""
        if not self.addons:
            raise ValueError("No modules specified for upgrade")

        options = self._prepare_params()
        # Replace install with upgrade
        for i, opt in enumerate(options):
            if opt == "-i":
                options[i] = "-u"
                break

        options.extend(["--stop-after-init", "--no-http"])

        cmd = [str(self._get_odoo_bin())] + options
        cmd.extend(DEFAULT_OPTS.split())

        print(f"Upgrading modules {','.join(self.addons)} in database '{self.db}'...")
        subprocess.run(cmd, check=True, env=self._get_venv_env())
