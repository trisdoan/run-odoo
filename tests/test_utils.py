import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess
import tempfile
import os

from run_odoo.utils import (
    install_dependecies_fedora,
    install_dependencies_debian,
    clone_or_update_repo
)


@pytest.mark.utils
@pytest.mark.fedora
@pytest.mark.subprocess
class TestFedoraDependencies:
    """Test Fedora dependency installation"""

    @patch('run_odoo.utils.subprocess.run')
    @patch('run_odoo.utils.Path')
    def test_install_dependencies_fedora_success(self, mock_path, mock_subprocess):
        """Test successful Fedora dependency installation"""
        # Mock the script path
        mock_script_path = MagicMock()
        mock_script_path.__str__.return_value = "/path/to/setup_script.sh"
        mock_path.return_value.parent.odoo.setup_script.sh = mock_script_path
        
        mock_subprocess.return_value = MagicMock()
        
        install_dependecies_fedora()
        
        # Verify chmod was called
        mock_subprocess.assert_any_call(
            "chmod +x /path/to/setup_script.sh",
            shell=True
        )
        
        # Verify script execution was called
        mock_subprocess.assert_any_call(
            [". /path/to/setup_script.sh"],
            shell=True,
            check=True
        )

    @patch('run_odoo.utils.subprocess.run')
    @patch('run_odoo.utils.Path')
    def test_install_dependencies_fedora_chmod_failure(self, mock_path, mock_subprocess):
        """Test Fedora dependency installation with chmod failure"""
        mock_script_path = MagicMock()
        mock_script_path.__str__.return_value = "/path/to/setup_script.sh"
        mock_path.return_value.parent.odoo.setup_script.sh = mock_script_path
        
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "chmod")
        
        with pytest.raises(subprocess.CalledProcessError):
            install_dependecies_fedora()

    @patch('run_odoo.utils.subprocess.run')
    @patch('run_odoo.utils.Path')
    def test_install_dependencies_fedora_script_failure(self, mock_path, mock_subprocess):
        """Test Fedora dependency installation with script execution failure"""
        mock_script_path = MagicMock()
        mock_script_path.__str__.return_value = "/path/to/setup_script.sh"
        mock_path.return_value.parent.odoo.setup_script.sh = mock_script_path
        
        # First call succeeds (chmod), second call fails (script execution)
        mock_subprocess.side_effect = [
            MagicMock(),  # chmod succeeds
            subprocess.CalledProcessError(1, ". /path/to/setup_script.sh")  # script fails
        ]
        
        with pytest.raises(subprocess.CalledProcessError):
            install_dependecies_fedora()


@pytest.mark.utils
@pytest.mark.debian
@pytest.mark.subprocess
class TestDebianDependencies:
    """Test Debian/Ubuntu dependency installation"""

    @patch('run_odoo.utils.subprocess.run')
    def test_install_dependencies_debian_success(self, mock_subprocess):
        """Test successful Debian dependency installation"""
        mock_subprocess.return_value = MagicMock()
        
        install_dependencies_debian()
        
        # Verify apt-get update was called
        mock_subprocess.assert_any_call(
            ["sudo", "apt-get", "update"],
            check=True
        )
        
        # Verify apt-get install was called with correct packages
        expected_packages = [
            "python3-dev", "libxml2-dev", "libxslt1-dev", "libevent-dev",
            "libsasl2-dev", "libldap2-dev", "libpq-dev", "libjpeg-dev",
            "libpng-dev", "libfreetype6-dev", "libffi-dev", "libssl-dev",
            "node-less", "postgresql-client"
        ]
        
        install_call = mock_subprocess.call_args_list[1]
        assert install_call[0][0] == ["sudo", "apt-get", "install", "-y"] + expected_packages
        assert install_call[1]["check"] is True

    @patch('run_odoo.utils.subprocess.run')
    def test_install_dependencies_debian_update_failure(self, mock_subprocess):
        """Test Debian dependency installation with update failure"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "apt-get update")
        
        with pytest.raises(subprocess.CalledProcessError):
            install_dependencies_debian()

    @patch('run_odoo.utils.subprocess.run')
    def test_install_dependencies_debian_install_failure(self, mock_subprocess):
        """Test Debian dependency installation with install failure"""
        # First call succeeds (update), second call fails (install)
        mock_subprocess.side_effect = [
            MagicMock(),  # apt-get update succeeds
            subprocess.CalledProcessError(1, "apt-get install")  # install fails
        ]
        
        with pytest.raises(subprocess.CalledProcessError):
            install_dependencies_debian()

    @patch('run_odoo.utils.subprocess.run')
    def test_install_dependencies_debian_error_message(self, mock_subprocess, capsys):
        """Test Debian dependency installation error message"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "apt-get install")
        
        with pytest.raises(subprocess.CalledProcessError):
            install_dependencies_debian()
        
        captured = capsys.readouterr()
        assert "Failed to install dependencies" in captured.out


@pytest.mark.utils
@pytest.mark.git
@pytest.mark.subprocess
class TestGitOperations:
    """Test git repository operations"""

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_new_clone(self, mock_subprocess):
        """Test cloning a new repository"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            branch = "main"
            
            clone_or_update_repo(repo_url, target_path, branch)
            
            # Verify git clone was called with correct parameters
            mock_subprocess.assert_called_once_with(
                ["git", "clone", repo_url, "-b", branch, str(target_path)],
                check=True
            )

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_existing_update(self, mock_subprocess):
        """Test updating an existing repository"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            branch = "main"
            
            # Create the target directory and .git subdirectory to simulate existing repo
            target_path.mkdir()
            (target_path / ".git").mkdir()
            
            clone_or_update_repo(repo_url, target_path, branch)
            
            # Verify git pull was called
            mock_subprocess.assert_called_once_with(
                ["git", "-C", str(target_path), "pull"],
                check=True
            )

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_default_branch(self, mock_subprocess):
        """Test cloning with default branch"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            
            clone_or_update_repo(repo_url, target_path)
            
            # Verify git clone was called with default branch "master"
            mock_subprocess.assert_called_once_with(
                ["git", "clone", repo_url, "-b", "master", str(target_path)],
                check=True
            )

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_clone_failure(self, mock_subprocess):
        """Test cloning with failure"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "git clone")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            
            with pytest.raises(subprocess.CalledProcessError):
                clone_or_update_repo(repo_url, target_path)

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_update_failure(self, mock_subprocess):
        """Test updating with failure"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "git pull")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            
            # Create the target directory and .git subdirectory to simulate existing repo
            target_path.mkdir()
            (target_path / ".git").mkdir()
            
            with pytest.raises(subprocess.CalledProcessError):
                clone_or_update_repo(repo_url, target_path)

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_parent_directory_creation(self, mock_subprocess):
        """Test that parent directory is created if it doesn't exist"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path with non-existent parent directories
            target_path = Path(temp_dir) / "nonexistent" / "parent" / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            
            clone_or_update_repo(repo_url, target_path)
            
            # Verify git clone was called (parent directories should be created)
            mock_subprocess.assert_called_once_with(
                ["git", "clone", repo_url, "-b", "master", str(target_path)],
                check=True
            )

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_output_messages(self, mock_subprocess, capsys):
        """Test that appropriate messages are printed during operations"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            
            clone_or_update_repo(repo_url, target_path)
            
            captured = capsys.readouterr()
            assert "Cloning" in captured.out
            assert repo_url in captured.out
            assert str(target_path) in captured.out

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_update_messages(self, mock_subprocess, capsys):
        """Test that update messages are printed for existing repositories"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            
            # Create the target directory and .git subdirectory to simulate existing repo
            target_path.mkdir()
            (target_path / ".git").mkdir()
            
            clone_or_update_repo(repo_url, target_path)
            
            captured = capsys.readouterr()
            assert "Updating" in captured.out
            assert str(target_path) in captured.out


@pytest.mark.utils
@pytest.mark.integration
class TestUtilsIntegration:
    """Test utility functions integration scenarios"""

    @patch('run_odoo.utils.subprocess.run')
    def test_full_dependency_installation_workflow(self, mock_subprocess):
        """Test complete dependency installation workflow"""
        mock_subprocess.return_value = MagicMock()
        
        # Test Fedora dependencies
        install_dependecies_fedora()
        
        # Test Debian dependencies
        install_dependencies_debian()
        
        # Verify multiple calls were made
        assert mock_subprocess.call_count >= 3  # At least chmod, script, apt-get update, apt-get install

    @patch('run_odoo.utils.subprocess.run')
    def test_git_operations_with_real_paths(self, mock_subprocess):
        """Test git operations with realistic paths"""
        mock_subprocess.return_value = MagicMock()
        
        # Test with realistic repository URLs and paths
        test_cases = [
            ("https://github.com/odoo/odoo.git", "odoo", "16.0"),
            ("git@github.com:odoo/enterprise.git", "enterprise", "17.0"),
            ("https://github.com/OCA/web.git", "web", "master"),
        ]
        
        for repo_url, repo_name, branch in test_cases:
            with tempfile.TemporaryDirectory() as temp_dir:
                target_path = Path(temp_dir) / repo_name
                
                clone_or_update_repo(repo_url, target_path, branch)
                
                # Verify git clone was called with correct parameters
                mock_subprocess.assert_any_call(
                    ["git", "clone", repo_url, "-b", branch, str(target_path)],
                    check=True
                )

    @patch('run_odoo.utils.subprocess.run')
    def test_error_handling_consistency(self, mock_subprocess):
        """Test that error handling is consistent across utility functions"""
        # Test that all functions properly handle CalledProcessError
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "test command")
        
        # Fedora dependencies
        with pytest.raises(subprocess.CalledProcessError):
            install_dependecies_fedora()
        
        # Debian dependencies
        with pytest.raises(subprocess.CalledProcessError):
            install_dependencies_debian()
        
        # Git operations
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            with pytest.raises(subprocess.CalledProcessError):
                clone_or_update_repo("https://test.com/repo.git", target_path)

    def test_path_handling_consistency(self):
        """Test that path handling is consistent across utility functions"""
        # Test that all functions properly handle Path objects
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test"
            
            # Test that Path objects are handled correctly
            assert isinstance(test_path, Path)
            assert str(test_path).startswith(temp_dir)


@pytest.mark.utils
@pytest.mark.edge_case
class TestUtilsEdgeCases:
    """Test utility functions edge cases"""

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_empty_repo_url(self, mock_subprocess):
        """Test cloning with empty repository URL"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            
            # Should still work with empty URL (though not practical)
            clone_or_update_repo("", target_path)
            
            mock_subprocess.assert_called_once_with(
                ["git", "clone", "", "-b", "master", str(target_path)],
                check=True
            )

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_empty_branch(self, mock_subprocess):
        """Test cloning with empty branch name"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "test_repo"
            repo_url = "https://github.com/test/repo.git"
            
            # Should use empty branch name
            clone_or_update_repo(repo_url, target_path, "")
            
            mock_subprocess.assert_called_once_with(
                ["git", "clone", repo_url, "-b", "", str(target_path)],
                check=True
            )

    @patch('run_odoo.utils.subprocess.run')
    def test_clone_or_update_repo_special_characters_in_path(self, mock_subprocess):
        """Test cloning with special characters in path"""
        mock_subprocess.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create path with special characters
            target_path = Path(temp_dir) / "test repo (v1.0)"
            repo_url = "https://github.com/test/repo.git"
            
            clone_or_update_repo(repo_url, target_path)
            
            # Should handle special characters correctly
            mock_subprocess.assert_called_once_with(
                ["git", "clone", repo_url, "-b", "master", str(target_path)],
                check=True
            )

    @patch('run_odoo.utils.subprocess.run')
    def test_dependencies_with_sudo_failure(self, mock_subprocess):
        """Test dependency installation when sudo fails"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "sudo")
        
        with pytest.raises(subprocess.CalledProcessError):
            install_dependencies_debian()

    @patch('run_odoo.utils.subprocess.run')
    def test_dependencies_with_network_failure(self, mock_subprocess):
        """Test dependency installation with network failure"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "apt-get")
        
        with pytest.raises(subprocess.CalledProcessError):
            install_dependencies_debian()

    def test_path_object_compatibility(self):
        """Test that functions work with both string and Path objects"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with string path
            string_path = os.path.join(temp_dir, "test_repo")
            
            # Test with Path object
            path_object = Path(temp_dir) / "test_repo"
            
            # Both should be handled correctly
            assert isinstance(string_path, str)
            assert isinstance(path_object, Path)
            
            # Convert string to Path for consistency
            path_from_string = Path(string_path)
            assert isinstance(path_from_string, Path)
            assert str(path_from_string) == string_path 