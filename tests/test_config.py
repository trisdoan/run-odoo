from run_odoo import config
from run_odoo.config import (
    get_config_for_profile, 
    load_config, 
    _find_config_file,
    _search_cwd,
    _search_config,
    _sanity_check,
    ConfigFile,
    Profile,
    Config
)

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os


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


@pytest.mark.config
@pytest.mark.unit
class TestConfigFile:
    """Test ConfigFile class functionality"""

    def test_config_file_creation(self):
        """Test creating a ConfigFile instance"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""
[profile.test]
version = 16.0
addons = ["test_module"]
enterprise = false
""")
            config_path = Path(f.name)
        
        try:
            config_file = ConfigFile(config_path)
            assert config_file.path == config_path
            assert isinstance(config_file.configs, dict)
            assert "profile" in config_file.configs
        finally:
            os.unlink(config_path)

    def test_config_file_nonexistent(self):
        """Test ConfigFile with nonexistent file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.toml"
            config_file = ConfigFile(config_path)
            assert config_file.configs == {}

    def test_config_file_invalid_toml(self):
        """Test ConfigFile with invalid TOML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("invalid toml content [")
            config_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Invalid TOML configuration"):
                ConfigFile(config_path)
        finally:
            os.unlink(config_path)

    def test_config_file_update(self):
        """Test updating configuration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("""
[profile.test]
version = 16.0
""")
            config_path = Path(f.name)
        
        try:
            config_file = ConfigFile(config_path)
            new_config = {
                "profile": {
                    "new_profile": {
                        "version": 17.0,
                        "addons": ["new_module"]
                    }
                }
            }
            config_file.update(new_config)
            assert "new_profile" in config_file.configs["profile"]
        finally:
            os.unlink(config_path)

    def test_config_file_write(self):
        """Test writing configuration to file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("")
            config_path = Path(f.name)
        
        try:
            config_file = ConfigFile(config_path)
            config_file.configs = {
                "profile": {
                    "test": {
                        "version": 16.0,
                        "addons": ["test_module"]
                    }
                }
            }
            config_file.write()
            
            # Verify file was written
            with open(config_path, 'r') as f:
                content = f.read()
                assert "version = 16.0" in content
                assert "test_module" in content
        finally:
            os.unlink(config_path)


@pytest.mark.config
@pytest.mark.unit
class TestConfigDiscovery:
    """Test configuration file discovery"""

    def test_search_cwd_found(self):
        """Test finding config file in current working directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / ".run_odoo.toml"
            config_path.write_text("[profile.test]\nversion = 16.0")
            
            with patch('run_odoo.config.Path.cwd', return_value=Path(temp_dir)):
                result = _search_cwd()
                assert result == config_path

    def test_search_cwd_not_found(self):
        """Test when no config file exists in current working directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('run_odoo.config.Path.cwd', return_value=Path(temp_dir)):
                result = _search_cwd()
                assert result is None

    def test_search_cwd_multiple_files(self):
        """Test finding config file when multiple options exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create both possible config files
            config_path1 = Path(temp_dir) / "run_odoo.toml"
            config_path2 = Path(temp_dir) / ".run_odoo.toml"
            config_path1.write_text("[profile.test1]\nversion = 16.0")
            config_path2.write_text("[profile.test2]\nversion = 17.0")
            
            with patch('run_odoo.config.Path.cwd', return_value=Path(temp_dir)):
                result = _search_cwd()
                # Should return the first one found (run_odoo.toml)
                assert result == config_path1

    @patch('run_odoo.config.user_config_path')
    def test_search_config_found(self, mock_user_config_path):
        """Test finding config file in user config directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "run_odoo"
            config_dir.mkdir()
            config_path = config_dir / ".run_odoo.toml"
            config_path.write_text("[profile.test]\nversion = 16.0")
            
            mock_user_config_path.return_value = config_dir
            result = _search_config()
            assert result == config_path

    @patch('run_odoo.config.user_config_path')
    def test_search_config_not_found(self, mock_user_config_path):
        """Test when no config file exists in user config directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "run_odoo"
            config_dir.mkdir()
            
            mock_user_config_path.return_value = config_dir
            result = _search_config()
            assert result is None


@pytest.mark.config
@pytest.mark.unit
class TestConfigLoading:
    """Test configuration loading functionality"""

    def test_find_config_file_specified_path(self):
        """Test finding config file with specified path"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("[profile.test]\nversion = 16.0")
            config_path = Path(f.name)
        
        try:
            result = _find_config_file(config_path)
            assert isinstance(result, dict)
            assert "profile" in result
        finally:
            os.unlink(config_path)

    def test_find_config_file_nonexistent_path(self):
        """Test finding config file with nonexistent specified path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.toml"
            with pytest.raises(FileNotFoundError):
                _find_config_file(config_path)

    @patch('run_odoo.config._search_cwd')
    @patch('run_odoo.config._search_config')
    def test_find_config_file_discovery(self, mock_search_config, mock_search_cwd):
        """Test finding config file through discovery"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("[profile.test]\nversion = 16.0")
            config_path = Path(f.name)
        
        try:
            mock_search_cwd.return_value = config_path
            mock_search_config.return_value = None
            
            result = _find_config_file(None)
            assert isinstance(result, dict)
            assert "profile" in result
            
            mock_search_cwd.assert_called_once()
            mock_search_config.assert_not_called()
        finally:
            os.unlink(config_path)

    @patch('run_odoo.config._search_cwd')
    @patch('run_odoo.config._search_config')
    def test_find_config_file_fallback(self, mock_search_config, mock_search_cwd):
        """Test finding config file with fallback to user config"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("[profile.test]\nversion = 16.0")
            config_path = Path(f.name)
        
        try:
            mock_search_cwd.return_value = None
            mock_search_config.return_value = config_path
            
            result = _find_config_file(None)
            assert isinstance(result, dict)
            assert "profile" in result
            
            mock_search_cwd.assert_called_once()
            mock_search_config.assert_called_once()
        finally:
            os.unlink(config_path)

    @patch('run_odoo.config._search_cwd')
    @patch('run_odoo.config._search_config')
    def test_find_config_file_not_found(self, mock_search_config, mock_search_cwd):
        """Test finding config file when none exists"""
        mock_search_cwd.return_value = None
        mock_search_config.return_value = None
        
        result = _find_config_file(None)
        assert result == {}


@pytest.mark.config
@pytest.mark.unit
class TestProfileManagement:
    """Test profile management functionality"""

    def test_get_config_for_profile_specific(self):
        """Test getting specific profile configuration"""
        config_data = {
            "profile": {
                "test_profile": {
                    "version": 16.0,
                    "addons": ["test_module"],
                    "enterprise": False
                },
                "other_profile": {
                    "version": 17.0,
                    "addons": ["other_module"],
                    "enterprise": True
                }
            }
        }
        
        with patch('run_odoo.config.load_config', return_value=config_data):
            profile = get_config_for_profile(None, "test_profile")
            assert profile["version"] == 16.0
            assert profile["addons"] == ["test_module"]
            assert profile["enterprise"] is False

    def test_get_config_for_profile_nonexistent(self):
        """Test getting nonexistent profile"""
        config_data = {
            "profile": {
                "existing_profile": {
                    "version": 16.0
                }
            }
        }
        
        with patch('run_odoo.config.load_config', return_value=config_data):
            with pytest.raises(ValueError, match="Profile 'nonexistent' not found"):
                get_config_for_profile(None, "nonexistent")

    def test_get_config_for_profile_no_profile_specified(self):
        """Test getting profile when none specified"""
        config_data = {
            "profile": {
                "first_profile": {
                    "version": 16.0,
                    "addons": ["first_module"]
                },
                "second_profile": {
                    "version": 17.0,
                    "addons": ["second_module"]
                }
            }
        }
        
        with patch('run_odoo.config.load_config', return_value=config_data):
            profile = get_config_for_profile(None, None)
            # Should return first profile
            assert profile["version"] == 16.0
            assert profile["addons"] == ["first_module"]

    def test_get_config_for_profile_no_profiles(self):
        """Test getting profile when no profiles exist"""
        config_data = {}
        
        with patch('run_odoo.config.load_config', return_value=config_data):
            profile = get_config_for_profile(None, None)
            assert profile == {}

    def test_get_config_for_profile_empty_profiles(self):
        """Test getting profile when profiles section is empty"""
        config_data = {"profile": {}}
        
        with patch('run_odoo.config.load_config', return_value=config_data):
            profile = get_config_for_profile(None, None)
            assert profile == {}


@pytest.mark.config
@pytest.mark.unit
@pytest.mark.error
class TestConfigValidation:
    """Test configuration validation"""

    def test_sanity_check_valid_config(self):
        """Test validation of valid configuration"""
        config_data = {
            "profile": {
                "test_profile": {
                    "version": 16.0,
                    "addons": ["test_module"]
                }
            }
        }
        
        # Should not raise any exception
        _sanity_check(config_data)

    def test_sanity_check_invalid_config_type(self):
        """Test validation of invalid config type"""
        with pytest.raises(ValueError, match="Configuration must be a dictionary"):
            _sanity_check("not a dict")

    def test_sanity_check_invalid_profiles_type(self):
        """Test validation of invalid profiles type"""
        config_data = {"profile": "not a dict"}
        
        with pytest.raises(ValueError, match="Profiles must be a dictionary"):
            _sanity_check(config_data)

    def test_sanity_check_invalid_profile_type(self):
        """Test validation of invalid profile type"""
        config_data = {
            "profile": {
                "test_profile": "not a dict"
            }
        }
        
        with pytest.raises(ValueError, match="Profile 'test_profile' must be a dictionary"):
            _sanity_check(config_data)

    def test_sanity_check_invalid_version_type(self):
        """Test validation of invalid version type"""
        config_data = {
            "profile": {
                "test_profile": {
                    "version": "not a number",
                    "addons": ["test_module"]
                }
            }
        }
        
        with pytest.raises(ValueError, match="Version in profile 'test_profile' must be a number"):
            _sanity_check(config_data)

    def test_sanity_check_valid_version_float(self):
        """Test validation of valid float version"""
        config_data = {
            "profile": {
                "test_profile": {
                    "version": 16.0,
                    "addons": ["test_module"]
                }
            }
        }
        
        # Should not raise any exception
        _sanity_check(config_data)

    def test_sanity_check_valid_version_int(self):
        """Test validation of valid integer version"""
        config_data = {
            "profile": {
                "test_profile": {
                    "version": 16,
                    "addons": ["test_module"]
                }
            }
        }
        
        # Should not raise any exception
        _sanity_check(config_data)

    def test_sanity_check_no_profiles(self):
        """Test validation of config without profiles"""
        config_data = {}
        
        # Should not raise any exception
        _sanity_check(config_data)

    def test_sanity_check_no_version(self):
        """Test validation of profile without version"""
        config_data = {
            "profile": {
                "test_profile": {
                    "addons": ["test_module"]
                }
            }
        }
        
        # Should not raise any exception
        _sanity_check(config_data)


@pytest.mark.config
@pytest.mark.integration
class TestConfigIntegration:
    """Test integration scenarios"""

    def test_full_config_workflow(self):
        """Test complete configuration workflow"""
        config_content = """
[profile.development]
version = 16.0
addons = ["sale", "purchase"]
enterprise = false
db = "dev_db"
http_port = 8069
log_level = "info"

[profile.production]
version = 17.0
addons = ["sale", "purchase", "inventory"]
enterprise = true
db = "prod_db"
http_port = 8080
log_level = "warn"
workers = 4
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = Path(f.name)
        
        try:
            # Test loading config
            config_data = load_config(config_path)
            assert "profile" in config_data
            assert "development" in config_data["profile"]
            assert "production" in config_data["profile"]
            
            # Test getting specific profile
            dev_profile = get_config_for_profile(config_path, "development")
            assert dev_profile["version"] == 16.0
            assert dev_profile["addons"] == ["sale", "purchase"]
            assert dev_profile["enterprise"] is False
            assert dev_profile["db"] == "dev_db"
            assert dev_profile["http_port"] == 8069
            assert dev_profile["log_level"] == "info"
            
            prod_profile = get_config_for_profile(config_path, "production")
            assert prod_profile["version"] == 17.0
            assert prod_profile["addons"] == ["sale", "purchase", "inventory"]
            assert prod_profile["enterprise"] is True
            assert prod_profile["db"] == "prod_db"
            assert prod_profile["http_port"] == 8080
            assert prod_profile["log_level"] == "warn"
            assert prod_profile["workers"] == 4
            
            # Test validation
            _sanity_check(config_data)
            
        finally:
            os.unlink(config_path)

    def test_config_with_all_profile_fields(self):
        """Test configuration with all possible profile fields"""
        config_content = """
[profile.complete]
version = 18.0
python_version = "3.12.0"
addons = ["base", "web", "sale"]
enterprise = true
themes = true
db = "complete_db"
path = "/custom/path"
extra_params = "--dev=all --test-enable"
http_port = 9090
log_level = "debug"
workers = 8
max_cron_threads = 2
db_host = "custom_host"
db_user = "custom_user"
db_password = "custom_password"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = Path(f.name)
        
        try:
            config_data = load_config(config_path)
            profile = get_config_for_profile(config_path, "complete")
            
            # Verify all fields are present
            expected_fields = [
                "version", "python_version", "addons", "enterprise", "themes",
                "db", "path", "extra_params", "http_port", "log_level", "workers",
                "max_cron_threads", "db_host", "db_user", "db_password"
            ]
            
            for field in expected_fields:
                assert field in profile
            
            # Verify specific values
            assert profile["version"] == 18.0
            assert profile["python_version"] == "3.12.0"
            assert profile["addons"] == ["base", "web", "sale"]
            assert profile["enterprise"] is True
            assert profile["themes"] is True
            assert profile["db"] == "complete_db"
            assert profile["path"] == "/custom/path"
            assert profile["extra_params"] == "--dev=all --test-enable"
            assert profile["http_port"] == 9090
            assert profile["log_level"] == "debug"
            assert profile["workers"] == 8
            assert profile["max_cron_threads"] == 2
            assert profile["db_host"] == "custom_host"
            assert profile["db_user"] == "custom_user"
            assert profile["db_password"] == "custom_password"
            
        finally:
            os.unlink(config_path)
