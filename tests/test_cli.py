import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

from run_odoo.cli import app


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def mock_runner():
    with patch('run_odoo.cli.Runner') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.cli
@pytest.mark.unit
class TestTryModule:
    """Test the try_module command"""

    def test_try_module_basic(self, cli_runner, mock_runner):
        """Test basic try_module command with minimal arguments"""
        result = cli_runner.invoke(app, ["try-module", "test_module"])
        
        assert result.exit_code == 0
        mock_runner.run.assert_called_once()

    def test_try_module_with_version(self, cli_runner, mock_runner):
        """Test try_module with specific version"""
        result = cli_runner.invoke(app, ["try-module", "test_module", "16.0"])
        
        assert result.exit_code == 0
        mock_runner.run.assert_called_once()

    def test_try_module_with_enterprise(self, cli_runner, mock_runner):
        """Test try_module with enterprise flag"""
        result = cli_runner.invoke(app, ["try-module", "test_module", "--enterprise"])
        
        assert result.exit_code == 0
        mock_runner.run.assert_called_once()

    def test_try_module_with_themes(self, cli_runner, mock_runner):
        """Test try_module with themes flag"""
        result = cli_runner.invoke(app, ["try-module", "test_module", "--themes"])
        
        assert result.exit_code == 0
        mock_runner.run.assert_called_once()

    def test_try_module_with_custom_port(self, cli_runner, mock_runner):
        """Test try_module with custom port"""
        result = cli_runner.invoke(app, ["try-module", "test_module", "--port", "8080"])
        
        assert result.exit_code == 0
        mock_runner.run.assert_called_once()

    def test_try_module_with_custom_db(self, cli_runner, mock_runner):
        """Test try_module with custom database name"""
        result = cli_runner.invoke(app, ["try-module", "test_module", "--db", "test_db"])
        
        assert result.exit_code == 0
        mock_runner.run.assert_called_once()

    def test_try_module_with_workers(self, cli_runner, mock_runner):
        """Test try_module with workers configuration"""
        result = cli_runner.invoke(app, ["try-module", "test_module", "--workers", "2"])
        
        assert result.exit_code == 0
        mock_runner.run.assert_called_once()

    def test_try_module_with_log_level(self, cli_runner, mock_runner):
        """Test try_module with custom log level"""
        result = cli_runner.invoke(app, ["try-module", "test_module", "--log-level", "debug"])
        
        assert result.exit_code == 0
        mock_runner.run.assert_called_once()

    @patch('run_odoo.cli.get_config_for_profile')
    def test_try_module_with_profile(self, mock_get_config, cli_runner, mock_runner):
        """Test try_module with profile configuration"""
        mock_config = {
            "addons": ["profile_module"],
            "version": 17.0,
            "enterprise": True,
            "db": "profile_db"
        }
        mock_get_config.return_value = mock_config
        
        result = cli_runner.invoke(app, ["try-module", "test_module", "--profile", "test_profile"])
        
        assert result.exit_code == 0
        mock_get_config.assert_called_once_with(config_path=None, profile_name="test_profile")
        mock_runner.run.assert_called_once()

    @patch('run_odoo.cli._search_cwd')
    @patch('run_odoo.cli.load_config')
    def test_try_module_with_local_config(self, mock_load_config, mock_search_cwd, cli_runner, mock_runner):
        """Test try_module with local configuration file"""
        mock_config = {
            "addons": ["local_module"],
            "version": 16.0,
            "enterprise": False
        }
        mock_load_config.return_value = mock_config
        mock_search_cwd.return_value = Path("/tmp/test_config.toml")
        
        result = cli_runner.invoke(app, ["try-module", "test_module"])
        
        assert result.exit_code == 0
        mock_search_cwd.assert_called_once()
        mock_load_config.assert_called_once()
        mock_runner.run.assert_called_once()


@pytest.mark.cli
@pytest.mark.unit
class TestTestModule:
    """Test the test_module command"""

    def test_test_module_basic(self, cli_runner, mock_runner):
        """Test basic test_module command"""
        result = cli_runner.invoke(app, ["test-module", "test_module"])
        
        assert result.exit_code == 0
        mock_runner.run_tests.assert_called_once()

    def test_test_module_with_version(self, cli_runner, mock_runner):
        """Test test_module with specific version"""
        result = cli_runner.invoke(app, ["test-module", "test_module", "16.0"])
        
        assert result.exit_code == 0
        mock_runner.run_tests.assert_called_once()

    def test_test_module_with_enterprise(self, cli_runner, mock_runner):
        """Test test_module with enterprise flag"""
        result = cli_runner.invoke(app, ["test-module", "test_module", "--enterprise"])
        
        assert result.exit_code == 0
        mock_runner.run_tests.assert_called_once()

    def test_test_module_with_custom_db(self, cli_runner, mock_runner):
        """Test test_module with custom database"""
        result = cli_runner.invoke(app, ["test-module", "test_module", "--db", "test_db"])
        
        assert result.exit_code == 0
        mock_runner.run_tests.assert_called_once()

    @patch('run_odoo.cli.get_config_for_profile')
    def test_test_module_with_profile(self, mock_get_config, cli_runner, mock_runner):
        """Test test_module with profile configuration"""
        mock_config = {
            "addons": ["profile_module"],
            "version": 17.0,
            "enterprise": True,
            "db": "profile_db"
        }
        mock_get_config.return_value = mock_config
        
        result = cli_runner.invoke(app, ["test-module", "test_module", "--profile", "test_profile"])
        
        assert result.exit_code == 0
        mock_get_config.assert_called_once_with(config_path=None, profile_name="test_profile")
        mock_runner.run_tests.assert_called_once()


@pytest.mark.cli
@pytest.mark.unit
class TestUpgradeModule:
    """Test the upgrade_module command"""

    def test_upgrade_module_basic(self, cli_runner, mock_runner):
        """Test basic upgrade_module command"""
        result = cli_runner.invoke(app, ["upgrade-module", "test_module"])
        
        assert result.exit_code == 0
        mock_runner.upgrade_modules.assert_called_once()

    def test_upgrade_module_with_version(self, cli_runner, mock_runner):
        """Test upgrade_module with specific version"""
        result = cli_runner.invoke(app, ["upgrade-module", "test_module", "16.0"])
        
        assert result.exit_code == 0
        mock_runner.upgrade_modules.assert_called_once()

    def test_upgrade_module_with_enterprise(self, cli_runner, mock_runner):
        """Test upgrade_module with enterprise flag"""
        result = cli_runner.invoke(app, ["upgrade-module", "test_module", "--enterprise"])
        
        assert result.exit_code == 0
        mock_runner.upgrade_modules.assert_called_once()

    def test_upgrade_module_with_custom_db(self, cli_runner, mock_runner):
        """Test upgrade_module with custom database"""
        result = cli_runner.invoke(app, ["upgrade-module", "test_module", "--db", "test_db"])
        
        assert result.exit_code == 0
        mock_runner.upgrade_modules.assert_called_once()

    @patch('run_odoo.cli.get_config_for_profile')
    def test_upgrade_module_with_profile(self, mock_get_config, cli_runner, mock_runner):
        """Test upgrade_module with profile configuration"""
        mock_config = {
            "addons": ["profile_module"],
            "version": 17.0,
            "enterprise": True,
            "db": "profile_db"
        }
        mock_get_config.return_value = mock_config
        
        result = cli_runner.invoke(app, ["upgrade-module", "test_module", "--profile", "test_profile"])
        
        assert result.exit_code == 0
        mock_get_config.assert_called_once_with(config_path=None, profile_name="test_profile")
        mock_runner.upgrade_modules.assert_called_once()


@pytest.mark.cli
@pytest.mark.unit
class TestShell:
    """Test the shell command"""

    def test_shell_basic(self, cli_runner, mock_runner):
        """Test basic shell command"""
        result = cli_runner.invoke(app, ["shell"])
        
        assert result.exit_code == 0
        mock_runner.run_shell.assert_called_once()

    def test_shell_with_module(self, cli_runner, mock_runner):
        """Test shell with specific module"""
        result = cli_runner.invoke(app, ["shell", "test_module"])
        
        assert result.exit_code == 0
        mock_runner.run_shell.assert_called_once()

    def test_shell_with_version(self, cli_runner, mock_runner):
        """Test shell with specific version"""
        result = cli_runner.invoke(app, ["shell", "test_module", "16.0"])
        
        assert result.exit_code == 0
        mock_runner.run_shell.assert_called_once()

    def test_shell_with_enterprise(self, cli_runner, mock_runner):
        """Test shell with enterprise flag"""
        result = cli_runner.invoke(app, ["shell", "--enterprise"])
        
        assert result.exit_code == 0
        mock_runner.run_shell.assert_called_once()

    def test_shell_with_custom_db(self, cli_runner, mock_runner):
        """Test shell with custom database"""
        result = cli_runner.invoke(app, ["shell", "--db", "test_db"])
        
        assert result.exit_code == 0
        mock_runner.run_shell.assert_called_once()

    @patch('run_odoo.cli.get_config_for_profile')
    def test_shell_with_profile(self, mock_get_config, cli_runner, mock_runner):
        """Test shell with profile configuration"""
        mock_config = {
            "addons": ["profile_module"],
            "version": 17.0,
            "enterprise": True,
            "db": "profile_db"
        }
        mock_get_config.return_value = mock_config
        
        result = cli_runner.invoke(app, ["shell", "--profile", "test_profile"])
        
        assert result.exit_code == 0
        mock_get_config.assert_called_once_with(config_path=None, profile_name="test_profile")
        mock_runner.run_shell.assert_called_once()


@pytest.mark.cli
@pytest.mark.unit
@pytest.mark.subprocess
class TestHarlequin:
    """Test the harlequin command"""

    @patch('run_odoo.cli.subprocess.run')
    def test_harlequin_basic(self, mock_subprocess, cli_runner):
        """Test basic harlequin command"""
        mock_subprocess.return_value = MagicMock()
        
        result = cli_runner.invoke(app, ["harlequin", "test_db"])
        
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        # Check that harlequin was called with correct connection string
        call_args = mock_subprocess.call_args[0][0]
        assert call_args[0] == "harlequin"
        assert "postgresql://openerp:openerp@localhost:5432/test_db" in call_args[1]

    @patch('run_odoo.cli.subprocess.run')
    def test_harlequin_with_custom_connection(self, mock_subprocess, cli_runner):
        """Test harlequin with custom connection parameters"""
        mock_subprocess.return_value = MagicMock()
        
        result = cli_runner.invoke(app, [
            "harlequin", "test_db",
            "--host", "custom_host",
            "--port", "5433",
            "--user", "custom_user",
            "--password", "custom_pass"
        ])
        
        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "postgresql://custom_user:custom_pass@custom_host:5433/test_db" in call_args[1]

    @patch('run_odoo.cli.get_config_for_profile')
    @patch('run_odoo.cli.subprocess.run')
    def test_harlequin_with_profile(self, mock_subprocess, mock_get_config, cli_runner):
        """Test harlequin with profile configuration"""
        mock_config = {
            "db": "profile_db",
            "db_host": "profile_host",
            "db_user": "profile_user",
            "db_password": "profile_pass"
        }
        mock_get_config.return_value = mock_config
        mock_subprocess.return_value = MagicMock()
        
        result = cli_runner.invoke(app, ["harlequin", "--profile", "test_profile"])
        
        assert result.exit_code == 0
        mock_get_config.assert_called_once_with(config_path=None, profile_name="test_profile")
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "postgresql://profile_user:profile_pass@profile_host:5432/profile_db" in call_args[1]

    @patch('run_odoo.cli.subprocess.run')
    def test_harlequin_missing_db(self, mock_subprocess, cli_runner):
        """Test harlequin without database name"""
        mock_subprocess.return_value = MagicMock()
        
        result = cli_runner.invoke(app, ["harlequin"])
        
        assert result.exit_code != 0
        assert "Database name is required" in result.stdout

    @patch('run_odoo.cli.subprocess.run')
    def test_harlequin_not_installed(self, mock_subprocess, cli_runner):
        """Test harlequin when not installed"""
        mock_subprocess.side_effect = FileNotFoundError()
        
        result = cli_runner.invoke(app, ["harlequin", "test_db"])
        
        assert result.exit_code == 1
        assert "Harlequin is not installed" in result.stdout

    @patch('run_odoo.cli.subprocess.run')
    def test_harlequin_process_error(self, mock_subprocess, cli_runner):
        """Test harlequin when process fails"""
        from subprocess import CalledProcessError
        mock_subprocess.side_effect = CalledProcessError(1, "harlequin")
        
        result = cli_runner.invoke(app, ["harlequin", "test_db"])
        
        assert result.exit_code == 1
        assert "Error starting Harlequin" in result.stdout


@pytest.mark.cli
@pytest.mark.error
class TestCLIErrorHandling:
    """Test CLI error handling"""

    @patch('run_odoo.cli.Runner')
    def test_runner_initialization_error(self, mock_runner_class, cli_runner):
        """Test handling of Runner initialization errors"""
        mock_runner_class.side_effect = ValueError("Invalid configuration")
        
        result = cli_runner.invoke(app, ["try-module", "test_module"])
        
        assert result.exit_code != 0

    @patch('run_odoo.cli.Runner')
    def test_runner_execution_error(self, mock_runner_class, cli_runner):
        """Test handling of Runner execution errors"""
        mock_runner = MagicMock()
        mock_runner.run.side_effect = Exception("Execution failed")
        mock_runner_class.return_value = mock_runner
        
        result = cli_runner.invoke(app, ["try-module", "test_module"])
        
        assert result.exit_code != 0

    @patch('run_odoo.cli.get_config_for_profile')
    def test_invalid_profile(self, mock_get_config, cli_runner):
        """Test handling of invalid profile"""
        mock_get_config.side_effect = ValueError("Profile not found")
        
        result = cli_runner.invoke(app, ["try-module", "test_module", "--profile", "invalid_profile"])
        
        assert result.exit_code != 0 