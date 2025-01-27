from run_odoo import config
from run_odoo.config import get_config_for_profile, load_config, _find_config_file

import pytest
from pathlib import Path


@pytest.mark.parametrize("filename", ["good_config.run_odoo.toml"])
def test_load_config(data_dir: Path, filename: str):
    good_config_path = data_dir / filename
    good_config = load_config(config_path=good_config_path)
    assert isinstance(good_config, dict)
    assert "profile" in good_config
    assert "mini-module" in good_config["profile"]
    assert good_config["profile"]["mini-module"]["addon"] == "eighteen_module"


@pytest.mark.parametrize("filename", ["good_config.run_odoo.toml"])
def test_load_named_profile(data_dir: Path, filename: str):
    good_config_path = data_dir / filename
    profile = get_config_for_profile(good_config_path, "mini-module")
    assert profile["version"] == 18.0


#
#
# def test_config_discovery():
#     pass
