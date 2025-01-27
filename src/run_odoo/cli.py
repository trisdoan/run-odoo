import typer

from typing_extensions import Annotated
from typing import Optional
from run_odoo.runner import Runner
from run_odoo.config import get_config_for_profile, _search_cwd, load_config
from typing import List
from pathlib import Path


app = typer.Typer()


@app.command()
def try_module(
    module: Annotated[str, typer.Argument(help="Module name to try")],
    version: Annotated[float, typer.Argument(help="Odoo version (e.g. 16.0)")] = 18.0,
    profile: Annotated[str, typer.Option(help="Profile name from config")] = "",
    db: Annotated[str, typer.Option(help="Database name")] = None,
    enterprise: Annotated[bool, typer.Option(help="Use Enterprise version")] = False,
    themes: Annotated[bool, typer.Option(help="Include theme modules")] = False,
    port: Annotated[int, typer.Option(help="HTTP port")] = 8069,
    log_level: Annotated[str, typer.Option(help="Log level")] = "warn",
    workers: Annotated[int, typer.Option(help="Number of workers")] = 0,
):
    if profile:
        config = get_config_for_profile(config_path=None, profile_name=profile)
    else:
        # Check for local config file
        if path := _search_cwd():
            config = load_config(path)
        else:
            config = {
                "version": version,
                "addons": [module],
                "enterprise": enterprise,
                "themes": themes,
                "db": db,
            }

    Runner(
        addons=config.get("addons", [module]),
        version=config.get("version", version),
        path=config.get("path", None),
        db=config.get("db", db),
        extra_params=config.get("extra_params", None),
        enterprise=config.get("enterprise", enterprise),
        themes=config.get("themes", themes),
        http_port=config.get("http_port", port),
        log_level=config.get("log_level", log_level),
        workers=config.get("workers", workers),
    ).run()


@app.command()
def test_module(
    module: Annotated[str, typer.Argument(help="Module name to test")],
    version: Annotated[float, typer.Argument(help="Odoo version (e.g. 16.0)")] = 18.0,
    profile: Annotated[str, typer.Option()] = "",
    db: Annotated[str, typer.Option(help="Database name")] = None,
    enterprise: Annotated[bool, typer.Option(help="Use Enterprise version")] = False,
):
    """Run tests for a specific module"""
    if profile:
        config = get_config_for_profile(config_path=None, profile_name=profile)
    else:
        # Check for local config file
        if path := _search_cwd():
            config = load_config(path)
        else:
            # Use CLI arguments if no config found
            config = {
                "version": version,
                "addons": [module],
                "enterprise": enterprise,
                "db": db,
            }

    Runner(
        addons=config.get("addons", [module]),
        version=config.get("version", version),
        path=config.get("path", None),
        db=config.get("db", db),
        enterprise=config.get("enterprise", enterprise),
        extra_params=config.get("extra_params", None),
    ).run_tests()


@app.command()
def upgrade_module(
    module: Annotated[str, typer.Argument(help="Module name to upgrade")],
    version: Annotated[float, typer.Argument(help="Odoo version (e.g. 16.0)")] = 18.0,
    profile: Annotated[str, typer.Option()] = "",
    db: Annotated[str, typer.Option(help="Database name")] = None,
    enterprise: Annotated[bool, typer.Option(help="Use Enterprise version")] = False,
):
    """Upgrade a specific module in existing database"""
    if profile:
        config = get_config_for_profile(config_path=None, profile_name=profile)
    else:
        # Check for local config file
        if path := _search_cwd():
            config = load_config(path)
        else:
            # Use CLI arguments if no config found
            config = {
                "version": version,
                "addons": [module],
                "enterprise": enterprise,
                "db": db,
            }

    Runner(
        addons=config.get("addons", [module]),
        version=config.get("version", version),
        path=config.get("path", None),
        db=config.get("db", db),
        enterprise=config.get("enterprise", enterprise),
        extra_params=config.get("extra_params", None),
    ).upgrade_modules()


@app.command()
def shell(
    module: Annotated[str, typer.Argument(help="Module/database context")] = "base",
    version: Annotated[float, typer.Argument(help="Odoo version (e.g. 16.0)")] = 18.0,
    profile: Annotated[str, typer.Option()] = "",
    db: Annotated[str, typer.Option(help="Database name")] = None,
    enterprise: Annotated[bool, typer.Option(help="Use Enterprise version")] = False,
):
    """Start Odoo shell for a database"""
    if profile:
        config = get_config_for_profile(config_path=None, profile_name=profile)
    else:
        # Check for local config file
        if path := _search_cwd():
            config = load_config(path)
        else:
            # Use CLI arguments if no config found
            config = {
                "version": version,
                "addons": [module],
                "enterprise": enterprise,
                "db": db,
            }

    Runner(
        addons=config.get("addons", [module]),
        version=config.get("version", version),
        path=config.get("path", None),
        db=config.get("db", db),
        enterprise=config.get("enterprise", enterprise),
        extra_params=config.get("extra_params", None),
        install_modules=False,  # Don't install modules for shell
    ).run_shell()


@app.command()
def harlequin(
    db: Annotated[Optional[str], typer.Argument(help="Database name")] = None,
    profile: Annotated[str, typer.Option(help="Profile name from config")] = "",
    host: Annotated[str, typer.Option(help="Database host")] = "localhost",
    port: Annotated[int, typer.Option(help="Database port")] = 5432,
    user: Annotated[str, typer.Option(help="Database user")] = "openerp",
    password: Annotated[str, typer.Option(help="Database password")] = "openerp",
):
    """Start Harlequin SQL IDE for specified database"""
    try:
        import subprocess

        # Load profile configuration if specified
        if profile:
            config = get_config_for_profile(config_path=None, profile_name=profile)
            # Use profile database connection parameters if available
            host = config.get("db_host", host)
            user = config.get("db_user", user)
            password = config.get("db_password", password)
            # Use profile database name if not specified as argument
            if not db:
                db = config.get("db", db)
        else:
            # Check for local config file
            if path := _search_cwd():
                config = load_config(path)
                # Use config database connection parameters if available
                host = config.get("db_host", host)
                user = config.get("db_user", user)
                password = config.get("db_password", password)
                # Use config database name if not specified as argument
                if not db:
                    db = config.get("db", db)

        # Validate that we have a database name
        if not db:
            raise typer.BadParameter("Database name is required. Either specify it as an argument or include it in the profile configuration.")

        # Build connection string
        conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"

        # Try to run harlequin
        cmd = ["harlequin", conn_str]
        print(f"Starting Harlequin for database '{db}'...")
        subprocess.run(cmd, check=True)

    except FileNotFoundError:
        print(
            "Harlequin is not installed. Install it with: pip install harlequin[postgres]"
        )
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Harlequin: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
