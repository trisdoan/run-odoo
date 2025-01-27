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


# FIXME: enhance naming + other improvements (move this to other format)
PYTHON_VERSIONS = {
    "17.0": "3.12.0",  # https://github.com/odoo/odoo/issues/187021
    "16.0": "3.7.0",
}

ODOO_URL = "https://github.com/odoo/odoo.git"
ENT_ODOO_URL = "git@github.com:odoo/enterprise.git"
# FIXME: update db_user to odoo
DEFAULT_OPTS = " --db_host=localhost --db_user=openerpr --db_password=openerp --workers=0 --max-cron-threads=0 --limit-time-cpu=3600 --limit-time-real=3600"


# pew in venv-odoo18 /home/trobz/.local/share/virtualenvs/venv-odoo18/bin/odoo -d v18e_product_set_sell_only_by_packaging --db_host=localhost --db_user=openerp --db_password=openerp --load=web,base --workers=4 --max-cron-threads=0 --limit-time-cpu=3600 --limit-time-real=3600 --http-interface=0.0.0.0 --addons-path=/home/trobz/code/odoo/odoo/18.0/addons,/home/trobz/code/odoo/odoo/18.0/odoo/addons,/home/trobz/code/odoo/enterprise/18.0,/home/trobz/code/oca/product-attribute/18.0,/home/trobz/code/oca/queue/18.0,/home/trobz/code/oca/sale-workflow/18.0,/home/trobz/code/oca/purchase-workflow/18.0,/home/trobz/code/oca/server-tools/18.0,/home/trobz/code/oca/server-ux/18.0,/home/trobz/code/oca/web/18.0,/home/trobz/code/oca/stock-logistics-transport/18.0,/home/trobz/code/oca/account-invoicing/18.0,/home/trobz/code/oca/pos/18.0,/home/trobz/code/oca/server-backend/18.0,/home/trobz/code/oca/social/18.0,/home/trobz/code/oca/partner-contact/18.0,/home/trobz/code/oca/server-env/18.0,/home/trobz/code/oca/mail/18.0,/home/trobz/code/oca/storage/18.0,/home/trobz/code/oca/management-system/18.0,/home/trobz/code/oca/hr-holidays/18.0,/home/trobz/code/oca/connector/18.0,/home/trobz/code/oca/delivery-carrier/18.0,/home/trobz/code/oca/calendar/18.0,/home/trobz/code/oca/edi/18.0,/home/trobz/code/oca/community-data-files/18.0,/home/trobz/code/oca/stock-logistics-warehouse/18.0,/home/trobz/code/oca/payroll/18.0 --load=web,base --log-level=warn --log-handler=:DEBUG --log-handler=py.warnings:INFO --log-handler=PIL:INFO -i product_set_sell_only_by_packaging
#
@dataclass
class Runner:
    """
    Take params passed by profile or cli to run Odoo CLI
    """
    version: str
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
    extra_params: Optional[str] = None

    def __post_init__(self) -> None:
        self.sanity_check()
        self.home_dir = Path.home()
        self._prepare_env()
        self._prepare_params()

    # FIXME: implement
    def sanity_check(self):
        # REQUIRED PARAMS
        # addons, versions, paths(odoo, enterprise, themes, extra)
        # db
        pass

    # FIXME: improve
    def _prepare_params(self):
        self.options = ""

        # Build addons paths
        addon_paths = []
        # Add standard Odoo paths
        odoo_src_path = self.odoo_root_dir / "odoo"
        addon_paths.extend(
            [str(odoo_src_path / "addons"), str(self.odoo_root_dir / "addons")]
        )

        # Add custom paths if specified
        if self.path:
            if (self.path / "odoo").exists():
                addon_paths.extend(
                    [str(self.path / "addons"), str(self.path / "odoo" / "addons")]
                )
                # Add enterprise path if it exists
                if (self.path / "enterprise").exists():
                    addon_paths.append(str(self.path / "enterprise"))

        # Build addons string
        addons = ",".join(self.addons) if self.addons else ""

        # Base options
        self.options = f" --http-interface=0.0.0.0"  # Allow external connections
        self.options += " --load=web,base"  # Load essential modules

        # Add logging options
        self.options += " --log-level=warn"  # Default log level
        self.options += " --log-handler=:DEBUG"  # Debug for specific modules
        self.options += " --log-handler=py.warnings:INFO"

        # Add module and path options
        if addons:
            self.options += f" -i {addons}"
        if addon_paths:
            self.options += f" --addons-path={','.join(addon_paths)}"
        if self.db:
            self.options += f" -d {self.db}"

        return self.options + DEFAULT_OPTS

    # FIXME: improve readability: split into smaller funcs
    # FIXME: what if I need to inject more dependencies
    def _prepare_env(self):
        self.app_dir = user_config_path(
            appname="run_odoo", appauthor=False, ensure_exists=True
        )

        # NOTE: pull odoo odoo_src
        # FIXME: how about enterprise
        # FIXME: move it to app_data_dir?
        self.odoo_root_dir = self.app_dir / str(self.version)
        if not self.odoo_root_dir.exists():
            print("run pull odoo src")
            # FIXME: pull: maybe an util func to reuse in update odoo_src
            os.mkdir(self.odoo_root_dir)
            os.chdir(self.odoo_root_dir)
            # FIXME: check shallow clone: https://stackoverflow.com/questions/37531605/how-to-test-if-git-repository-is-shallow
            subprocess.run(
                ["git", "clone", f"{ODOO_URL}", "-b", f"{self.version}", "--quiet"]
            )
        else:
            # TODO: update branch?
            pass

        # NOTE: create env
        self.venvs_dir = self.home_dir / ".pyenv" / "versions"
        self.venv = f"venv-odoo{self.version}"
        # FIXME: what about venv exists but some packages are not installed yet
        # FIXME: check module python-packages required using manifestoo
        py_version = PYTHON_VERSIONS.get(self.version)
        try:
            subprocess.check_call(["pyenv", "local", f"{py_version}"])
        except subprocess.CalledProcessError:
            print("run install py")
            subprocess.call(["pyenv", "install", f"{py_version}"])

        self.venv_bin_path = self.venvs_dir / self.venv / "bin"
        print("self.venv_bin_path", self.venv_bin_path)
        if not self.venv_bin_path.exists():
            print("run create env")
            # create venv
            subprocess.run(f"pyenv virtualenv {py_version} {self.venv}", shell=True)
            # TODO: maybe use a class like strategy to handle this
            # install required packages, use https://github.com/python-distro/distro to identify the distro
            # if ubunto, run the script from odoo
            # if fedora, run setup_script: before run it, make it excutable, refer it in utils.py
            if distro.id() == "fedora":
                utils.install_dependecies_fedora()
            else:
                debinstall_path = self.odoo_root_dir / "odoo" / "setup"
                subprocess.run(f". {debinstall_path}/debinstall.sh")

            subprocess.run(
                f'{self.venvs_dir/self.venv}/bin/pip install -e "file://{self.app_dir/str(self.version)}/odoo#egg=odoo"',
                shell=True,
            )
            subprocess.run(
                f"{self.venvs_dir/self.venv}/bin/pip install -r {self.app_dir/str(self.version)}/odoo/requirements.txt",
                shell=True,
            )
        self.odoo_bin_path = self.venvs_dir / self.venv_bin_path / "odoo"

    # FIXME: improve code + how it visualize
    def run(self):
        # activate_env = f"{self.venv_bin_path}/activate"
        # odoo = f"{self.venv_bin_path}/python {self.odoo_bin_path} {self.options}"
        # command = f". {activate_env} && {odoo}"

        print("odoo", self.options)
        # subprocess.run(
        #     command,
        #     shell=True,
        # )
