import subprocess
from pathlib import Path


# FIXME: enhance this - add error handling and logging
def install_dependecies_fedora():
    """Install system dependencies for Odoo on Fedora"""
    script_path = Path(__file__).parent / "odoo" / "setup_script.sh"
    subprocess.run(
        f"chmod +x {script_path}",
        shell=True,
    )
    subprocess.run([f". {script_path}"], shell=True, check=True)


def install_dependencies_debian():
    """Install system dependencies for Odoo on Debian/Ubuntu"""
    # FIXME: implement debian/ubuntu dependency installation
    packages = [
        "python3-dev",
        "libxml2-dev",
        "libxslt1-dev",
        "libevent-dev",
        "libsasl2-dev",
        "libldap2-dev",
        "libpq-dev",
        "libjpeg-dev",
        "libpng-dev",
        "libfreetype6-dev",
        "libffi-dev",
        "libssl-dev",
        "node-less",
        "postgresql-client",
    ]

    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y"] + packages, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        raise


def clone_or_update_repo(repo_url: str, target_path: Path, branch: str = "master"):
    """Clone repository or update if it already exists"""
    # FIXME: implement git repository management utility
    if target_path.exists() and (target_path / ".git").exists():
        print(f"Updating {target_path}...")
        subprocess.run(["git", "-C", str(target_path), "pull"], check=True)
    else:
        print(f"Cloning {repo_url} to {target_path}...")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", repo_url, "-b", branch, str(target_path)], check=True
        )
