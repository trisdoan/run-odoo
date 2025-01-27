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
    version: Annotated[str, typer.Argument(help="Odoo version (e.g. 16.0)")] = "",
    profile: Annotated[str, typer.Option(help="Profile name from config")] = "",
    modules: Annotated[List[str], typer.Option("--module", "-m", help="Module(s) to install")] = None,
    db: Annotated[str, typer.Option(help="Database name")] = None,
    enterprise: Annotated[bool, typer.Option(help="Use Enterprise version")] = False,
    themes: Annotated[bool, typer.Option(help="Include theme modules")] = False,
    port: Annotated[int, typer.Option(help="HTTP port")] = 8069,
    log_level: Annotated[str, typer.Option(help="Log level")] = "warn",
    workers: Annotated[int, typer.Option(help="Number of workers")] = 0,
):
    """
    Run Odoo with specified configuration, either from profile or local config
    """
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
                "addons": modules,
                "enterprise": enterprise,
                "themes": themes,
            }

    Runner(
        addons=config.get("addons", modules),
        version=config.get("version", version),
        path=config.get("path", None),
        db=config.get("db", None),
        extra_params=config.get("extra_params", None),
    ).run()


@app.command()
def test_module(
    profile: Annotated[str, typer.Option()] = "",
):
    pass
    # Runner(
    #     profile,
    # ).run()


if __name__ == "__main__":
    app()
