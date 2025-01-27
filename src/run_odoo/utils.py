import subprocess
from pathlib import Path


# FIXME: enhance this
def install_dependecies_fedora():
    script_path = Path(__file__).parent / "odoo" / "setup_script.sh"
    subprocess.run(
        f"chmod +x {script_path}",
        shell=True,
    )
    subprocess.run([f". {script_path}"], shell=True)
