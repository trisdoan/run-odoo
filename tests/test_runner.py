import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import os
import subprocess

from run_odoo.runner import Runner, PYTHON_VERSIONS, ODOO_URL, ENT_ODOO_URL


@pytest.fixture
def mock_paths():
    """Mock common paths used in Runner"""
    with patch('run_odoo.runner.Path.home', return_value=Path('/home/test')):
        with patch('run_odoo.runner.user_config_path', return_value=Path('/tmp/run_odoo')):
            yield


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls"""
    with patch('run_odoo.runner.subprocess') as mock:
        yield mock


@pytest.mark.runner
@pytest.mark.unit
class TestRunnerInitialization:
    """Test Runner class initialization and validation"""

    def test_runner_basic_initialization(self, mock_paths):
        """Test basic Runner initialization"""
        runner = Runner(version=16.0)
        assert runner.version == 16.0
        assert runner.addons is None
        assert runner.db is None
        assert runner.enterprise is False
        assert runner.themes is False
        assert runner.log_level == "warn"
        assert runner.workers == 0
        assert runner.http_port == 8069
        assert runner.install_modules is True

    def test_runner_full_initialization(self, mock_paths):
        """Test Runner initialization with all parameters"""
        runner = Runner(
            version=17.0,
            addons=["sale", "purchase"],
            db="test_db",
            path=Path("/custom/path"),
            enterprise=True,
            themes=True,
            log_level="debug",
            workers=4,
            max_cron_threads=2,
            db_host="custom_host",
            db_user="custom_user",
            db_password="custom_pass",
            http_port=8080,
            http_interface="127.0.0.1",
            extra_params="--dev=all",
            install_modules=False,
            stop_after_init=True,
            test_enable=True
        )
        
        assert runner.version == 17.0
        assert runner.addons == ["sale", "purchase"]
        assert runner.db == "test_db"
        assert runner.path == Path("/custom/path")
        assert runner.enterprise is True
        assert runner.themes is True
        assert runner.log_level == "debug"
        assert runner.workers == 4
        assert runner.max_cron_threads == 2
        assert runner.db_host == "custom_host"
        assert runner.db_user == "custom_user"
        assert runner.db_password == "custom_pass"
        assert runner.http_port == 8080
        assert runner.http_interface == "127.0.0.1"
        assert runner.extra_params == "--dev=all"
        assert runner.install_modules is False
        assert runner.stop_after_init is True
        assert runner.test_enable is True

    def test_runner_missing_version(self, mock_paths):
        """Test Runner initialization without version"""
        with pytest.raises(ValueError, match="Odoo version is required"):
            Runner(version=None)

    def test_runner_unsupported_version(self, mock_paths):
        """Test Runner initialization with unsupported version"""
        with pytest.raises(ValueError, match="Unsupported Odoo version"):
            Runner(version=99.0)

    def test_runner_supported_versions(self, mock_paths):
        """Test Runner initialization with all supported versions"""
        for version in PYTHON_VERSIONS.keys():
            runner = Runner(version=version)
            assert runner.version == version

    def test_runner_warning_no_addons(self, mock_paths, capsys):
        """Test Runner initialization warning when no addons specified"""
        runner = Runner(version=16.0)
        captured = capsys.readouterr()
        assert "Warning: No modules specified for installation" in captured.out


@pytest.mark.runner
@pytest.mark.unit
@pytest.mark.subprocess
class TestRunnerEnvironmentSetup:
    """Test Runner environment setup methods"""

    @patch('run_odoo.runner.subprocess.run')
    @patch('run_odoo.runner.os.mkdir')
    @patch('run_odoo.runner.os.chdir')
    def test_setup_odoo_source_new(self, mock_chdir, mock_mkdir, mock_subprocess, mock_paths):
        """Test setting up Odoo source when it doesn't exist"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0)
        
        # Verify directories were created
        mock_mkdir.assert_called()
        mock_chdir.assert_called()
        mock_subprocess.assert_called()
        
        # Verify git clone was called with correct parameters
        clone_call = mock_subprocess.call_args_list[0]
        assert clone_call[0][0] == ["git", "clone", ODOO_URL, "-b", "16.0", "--quiet", "odoo"]

    @patch('run_odoo.runner.subprocess.run')
    @patch('run_odoo.runner.os.mkdir')
    @patch('run_odoo.runner.os.chdir')
    def test_setup_odoo_source_exists(self, mock_chdir, mock_mkdir, mock_subprocess, mock_paths):
        """Test setting up Odoo source when it already exists"""
        mock_subprocess.return_value = MagicMock()
        
        # Mock that the directory already exists
        with patch('run_odoo.runner.Path.exists', return_value=True):
            runner = Runner(version=16.0)
            
            # Should not create directories or clone
            mock_mkdir.assert_not_called()
            mock_chdir.assert_not_called()
            mock_subprocess.assert_not_called()

    @patch('run_odoo.runner.subprocess.run')
    def test_setup_enterprise_source_enabled(self, mock_subprocess, mock_paths):
        """Test setting up Enterprise source when enabled"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, enterprise=True)
        
        # Verify git clone was called for enterprise
        clone_call = mock_subprocess.call_args_list[0]
        assert clone_call[0][0] == ["git", "clone", ENT_ODOO_URL, "-b", "16.0", "--quiet", str(Path('/tmp/run_odoo/enterprise/16.0'))]

    @patch('run_odoo.runner.subprocess.run')
    def test_setup_enterprise_source_disabled(self, mock_subprocess, mock_paths):
        """Test setting up Enterprise source when disabled"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, enterprise=False)
        
        # Should not clone enterprise
        mock_subprocess.assert_not_called()

    @patch('run_odoo.runner.subprocess.run')
    @patch('run_odoo.runner.subprocess.check_call')
    def test_setup_virtual_environment_new(self, mock_check_call, mock_subprocess, mock_paths):
        """Test setting up virtual environment when it doesn't exist"""
        mock_subprocess.return_value = MagicMock()
        mock_check_call.return_value = 0
        
        # Mock pyenv versions to return empty list
        mock_subprocess.return_value.stdout = ""
        
        runner = Runner(version=16.0)
        
        # Verify pyenv commands were called
        mock_subprocess.assert_called()
        mock_check_call.assert_called()

    @patch('run_odoo.runner.subprocess.run')
    @patch('run_odoo.runner.subprocess.check_call')
    def test_setup_virtual_environment_exists(self, mock_check_call, mock_subprocess, mock_paths):
        """Test setting up virtual environment when it already exists"""
        mock_subprocess.return_value = MagicMock()
        mock_check_call.return_value = 0
        
        # Mock pyenv versions to return existing venv
        mock_subprocess.return_value.stdout = "venv-odoo16.0"
        
        runner = Runner(version=16.0)
        
        # Should not create new virtual environment
        mock_check_call.assert_not_called()

    @patch('run_odoo.runner.subprocess.run')
    def test_install_python_dependencies(self, mock_subprocess, mock_paths):
        """Test installing Python dependencies"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0)
        runner._install_python_dependencies()
        
        # Verify pip install commands were called
        assert mock_subprocess.call_count >= 1


@pytest.mark.runner
@pytest.mark.unit
class TestRunnerParameterBuilding:
    """Test Runner parameter building methods"""

    def test_prepare_params_basic(self, mock_paths):
        """Test basic parameter preparation"""
        runner = Runner(version=16.0, addons=["test_module"])
        options = runner._prepare_params()
        
        # Check that basic options are included
        assert "--http-port" in options
        assert "8069" in options
        assert "--log-level" in options
        assert "warn" in options
        assert "--workers" in options
        assert "0" in options

    def test_prepare_params_with_database(self, mock_paths):
        """Test parameter preparation with database"""
        runner = Runner(version=16.0, db="test_db")
        options = runner._prepare_params()
        
        assert "-d" in options
        assert "test_db" in options

    def test_prepare_params_with_addons(self, mock_paths):
        """Test parameter preparation with addons"""
        runner = Runner(version=16.0, addons=["sale", "purchase"])
        options = runner._prepare_params()
        
        assert "-i" in options
        assert "sale,purchase" in options

    def test_prepare_params_with_enterprise(self, mock_paths):
        """Test parameter preparation with enterprise"""
        runner = Runner(version=16.0, enterprise=True)
        options = runner._prepare_params()
        
        # Should include enterprise addons path
        addons_paths = [opt for opt in options if opt.startswith("--addons-path")]
        assert len(addons_paths) > 0

    def test_prepare_params_with_custom_path(self, mock_paths):
        """Test parameter preparation with custom path"""
        runner = Runner(version=16.0, path=Path("/custom/path"))
        options = runner._prepare_params()
        
        # Should include custom addons paths
        addons_paths = [opt for opt in options if opt.startswith("--addons-path")]
        assert len(addons_paths) > 0

    def test_prepare_params_with_extra_params(self, mock_paths):
        """Test parameter preparation with extra parameters"""
        runner = Runner(version=16.0, extra_params="--dev=all --test-enable")
        options = runner._prepare_params()
        
        assert "--dev=all" in options
        assert "--test-enable" in options

    def test_prepare_params_with_test_enable(self, mock_paths):
        """Test parameter preparation with test enable"""
        runner = Runner(version=16.0, test_enable=True)
        options = runner._prepare_params()
        
        assert "--test-enable" in options

    def test_prepare_params_with_stop_after_init(self, mock_paths):
        """Test parameter preparation with stop after init"""
        runner = Runner(version=16.0, stop_after_init=True)
        options = runner._prepare_params()
        
        assert "--stop-after-init" in options

    def test_prepare_params_without_install_modules(self, mock_paths):
        """Test parameter preparation without installing modules"""
        runner = Runner(version=16.0, addons=["test_module"], install_modules=False)
        options = runner._prepare_params()
        
        # Should not include install flag
        assert "-i" not in options

    def test_prepare_params_custom_http_settings(self, mock_paths):
        """Test parameter preparation with custom HTTP settings"""
        runner = Runner(
            version=16.0,
            http_port=8080,
            http_interface="127.0.0.1"
        )
        options = runner._prepare_params()
        
        assert "--http-port" in options
        assert "8080" in options
        assert "--http-interface" in options
        assert "127.0.0.1" in options

    def test_prepare_params_custom_log_settings(self, mock_paths):
        """Test parameter preparation with custom log settings"""
        runner = Runner(version=16.0, log_level="debug")
        options = runner._prepare_params()
        
        assert "--log-level" in options
        assert "debug" in options

    def test_prepare_params_worker_settings(self, mock_paths):
        """Test parameter preparation with worker settings"""
        runner = Runner(version=16.0, workers=4, max_cron_threads=2)
        options = runner._prepare_params()
        
        assert "--workers" in options
        assert "4" in options
        assert "--max-cron-threads" in options
        assert "2" in options


@pytest.mark.runner
@pytest.mark.unit
@pytest.mark.subprocess
class TestRunnerExecution:
    """Test Runner execution methods"""

    @patch('run_odoo.runner.subprocess.run')
    def test_run_basic(self, mock_subprocess, mock_paths):
        """Test basic run execution"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, addons=["test_module"])
        runner.run()
        
        # Verify subprocess was called
        mock_subprocess.assert_called_once()
        
        # Verify command structure
        cmd = mock_subprocess.call_args[0][0]
        assert "odoo-bin" in cmd[0]
        assert "-i" in cmd
        assert "test_module" in cmd

    @patch('run_odoo.runner.subprocess.run')
    def test_run_with_database(self, mock_subprocess, mock_paths):
        """Test run execution with database"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, db="test_db")
        runner.run()
        
        cmd = mock_subprocess.call_args[0][0]
        assert "-d" in cmd
        assert "test_db" in cmd

    @patch('run_odoo.runner.subprocess.run')
    def test_run_database_name_generation(self, mock_subprocess, mock_paths):
        """Test automatic database name generation"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, addons=["sale"])
        runner.run()
        
        # Should generate database name like v16c_sale
        assert runner.db == "v16c_sale"

    @patch('run_odoo.runner.subprocess.run')
    def test_run_enterprise_database_name(self, mock_subprocess, mock_paths):
        """Test database name generation for enterprise"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, addons=["sale"], enterprise=True)
        runner.run()
        
        # Should generate database name like v16e_sale
        assert runner.db == "v16e_sale"

    @patch('run_odoo.runner.subprocess.run')
    def test_run_keyboard_interrupt(self, mock_subprocess, mock_paths, capsys):
        """Test run execution with keyboard interrupt"""
        mock_subprocess.side_effect = KeyboardInterrupt()
        
        runner = Runner(version=16.0)
        
        # Should handle KeyboardInterrupt gracefully
        runner.run()
        captured = capsys.readouterr()
        assert "Odoo stopped by user" in captured.out

    @patch('run_odoo.runner.subprocess.run')
    def test_run_subprocess_error(self, mock_subprocess, mock_paths):
        """Test run execution with subprocess error"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "odoo")
        
        runner = Runner(version=16.0)
        
        with pytest.raises(subprocess.CalledProcessError):
            runner.run()

    @patch('run_odoo.runner.subprocess.run')
    def test_run_tests(self, mock_subprocess, mock_paths):
        """Test run_tests method"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, addons=["test_module"])
        runner.run_tests()
        
        # Should set test flags
        assert runner.test_enable is True
        assert runner.stop_after_init is True
        assert runner.workers == 0
        
        # Should call run method
        mock_subprocess.assert_called_once()

    @patch('run_odoo.runner.subprocess.run')
    def test_run_shell(self, mock_subprocess, mock_paths):
        """Test run_shell method"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, db="test_db")
        runner.run_shell()
        
        # Verify subprocess was called
        mock_subprocess.assert_called_once()
        
        # Verify command includes shell and no-http
        cmd = mock_subprocess.call_args[0][0]
        assert "shell" in cmd
        assert "--no-http" in cmd

    @patch('run_odoo.runner.subprocess.run')
    def test_upgrade_modules(self, mock_subprocess, mock_paths):
        """Test upgrade_modules method"""
        mock_subprocess.return_value = MagicMock()
        
        runner = Runner(version=16.0, addons=["test_module"])
        runner.upgrade_modules()
        
        # Verify subprocess was called
        mock_subprocess.assert_called_once()
        
        # Verify command includes upgrade and stop-after-init
        cmd = mock_subprocess.call_args[0][0]
        assert "-u" in cmd
        assert "--stop-after-init" in cmd
        assert "--no-http" in cmd

    def test_upgrade_modules_no_addons(self, mock_paths):
        """Test upgrade_modules without addons"""
        runner = Runner(version=16.0)
        
        with pytest.raises(ValueError, match="No modules specified for upgrade"):
            runner.upgrade_modules()


@pytest.mark.runner
@pytest.mark.unit
class TestRunnerUtilityMethods:
    """Test Runner utility methods"""

    def test_get_venv_env(self, mock_paths):
        """Test getting virtual environment environment variables"""
        runner = Runner(version=16.0)
        env = runner._get_venv_env()
        
        assert "VIRTUAL_ENV" in env
        assert "PATH" in env
        assert "venv-odoo16.0" in env["VIRTUAL_ENV"]

    def test_get_odoo_bin(self, mock_paths):
        """Test getting Odoo binary path"""
        runner = Runner(version=16.0)
        odoo_bin = runner._get_odoo_bin()
        
        assert odoo_bin.name == "odoo-bin"
        assert "odoo" in str(odoo_bin)


@pytest.mark.runner
@pytest.mark.integration
class TestRunnerIntegration:
    """Test Runner integration scenarios"""

    @patch('run_odoo.runner.subprocess.run')
    @patch('run_odoo.runner.subprocess.check_call')
    def test_full_runner_workflow(self, mock_check_call, mock_subprocess, mock_paths):
        """Test complete Runner workflow"""
        mock_subprocess.return_value = MagicMock()
        mock_check_call.return_value = 0
        
        # Mock pyenv to return existing environment
        mock_subprocess.return_value.stdout = "venv-odoo16.0"
        
        # Mock that directories exist
        with patch('run_odoo.runner.Path.exists', return_value=True):
            runner = Runner(
                version=16.0,
                addons=["sale", "purchase"],
                db="test_db",
                enterprise=True,
                log_level="debug",
                workers=2
            )
            
            # Test parameter preparation
            options = runner._prepare_params()
            assert "-d" in options
            assert "test_db" in options
            assert "-i" in options
            assert "sale,purchase" in options
            assert "--log-level" in options
            assert "debug" in options
            assert "--workers" in options
            assert "2" in options
            
            # Test execution
            runner.run()
            mock_subprocess.assert_called()

    @patch('run_odoo.runner.subprocess.run')
    def test_runner_with_all_features(self, mock_subprocess, mock_paths):
        """Test Runner with all features enabled"""
        mock_subprocess.return_value = MagicMock()
        
        # Mock that directories exist
        with patch('run_odoo.runner.Path.exists', return_value=True):
            runner = Runner(
                version=18.0,
                addons=["base", "web", "sale"],
                db="complete_db",
                path=Path("/custom/path"),
                enterprise=True,
                themes=True,
                log_level="debug",
                workers=4,
                max_cron_threads=2,
                db_host="custom_host",
                db_user="custom_user",
                db_password="custom_pass",
                http_port=8080,
                http_interface="127.0.0.1",
                extra_params="--dev=all --test-enable",
                install_modules=True,
                stop_after_init=False,
                test_enable=True
            )
            
            # Test all parameters are set correctly
            assert runner.version == 18.0
            assert runner.addons == ["base", "web", "sale"]
            assert runner.db == "complete_db"
            assert runner.path == Path("/custom/path")
            assert runner.enterprise is True
            assert runner.themes is True
            assert runner.log_level == "debug"
            assert runner.workers == 4
            assert runner.max_cron_threads == 2
            assert runner.db_host == "custom_host"
            assert runner.db_user == "custom_user"
            assert runner.db_password == "custom_pass"
            assert runner.http_port == 8080
            assert runner.http_interface == "127.0.0.1"
            assert runner.extra_params == "--dev=all --test-enable"
            assert runner.install_modules is True
            assert runner.stop_after_init is False
            assert runner.test_enable is True
            
            # Test parameter preparation includes all settings
            options = runner._prepare_params()
            assert "-d" in options
            assert "complete_db" in options
            assert "-i" in options
            assert "base,web,sale" in options
            assert "--log-level" in options
            assert "debug" in options
            assert "--workers" in options
            assert "4" in options
            assert "--max-cron-threads" in options
            assert "2" in options
            assert "--http-port" in options
            assert "8080" in options
            assert "--http-interface" in options
            assert "127.0.0.1" in options
            assert "--dev=all" in options
            assert "--test-enable" in options 