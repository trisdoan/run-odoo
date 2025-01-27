# Run Odoo

A Python CLI tool for easily running Odoo instances with automatic environment management.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Commands](#commands)
- [Environment Management](#environment-management)
- [Requirements](#requirements)
- [Development](#development)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Changelog](#changelog)
- [License](#license)

## ✨ Features

- **Auto-setup virtual environments**: Uses pyenv and virtualenv to manage Python environments for different Odoo versions
- **Profile-based configuration**: Easy management and sharing of running configurations via profiles
- **Harlequin integration**: Built-in SQL IDE support for database exploration

## 🚀 Installation

### Prerequisites

- Python 3.10+
- pyenv (for Python version management)
- Git
- PostgreSQL (for database)

### Install from source

```bash
git clone https://github.com/trisdoan/run-odoo.git
cd run-odoo
pip install -e .
```

### Install from PyPI


## 🏃‍♂️ Quick Start

### Try a module
```bash
# Try the 'sale' module in Odoo 18.0
run-odoo try-module sale 18.0

# Try with enterprise edition
run-odoo try-module sale 18.0 --enterprise
```

### Run tests
```bash
# Run tests for a specific module
run-odoo test-module sale 18.0
```

### Start a shell
```bash
# Start Odoo shell
run-odoo shell sale 18.0
```

### Upgrade modules
```bash
# Upgrade a module in existing database
run-odoo upgrade-module sale 18.0
```

### Database exploration with Harlequin
```bash
# Start Harlequin SQL IDE for a database
run-odoo harlequin my_database
```

## ⚙️ Configuration

Create a configuration file in your project directory or user config directory:

### `.run_odoo.toml` or `run_odoo.toml`

```toml
[profile.development]
addons = ["sale", "purchase", "stock"]
version = 18.0
enterprise = true
themes = false
http_port = 8069
workers = 4
log_level = "info"

[profile.testing]
addons = ["my_custom_module"]
version = 17.0
enterprise = false
http_port = 8070
workers = 0
```

### Using profiles

```bash
# Use a specific profile
run-odoo try-module --profile development

# Profile settings override command line arguments
run-odoo test-module --profile testing
```

## 📖 Commands

| Command | Description |
|---------|-------------|
| `try-module MODULE [VERSION]` | Start Odoo and install the specified module |
| `test-module MODULE [VERSION]` | Run tests for the specified module |
| `upgrade-module MODULE [VERSION]` | Upgrade the specified module in existing database |
| `shell [MODULE] [VERSION]` | Start Odoo shell for database exploration |
| `harlequin DATABASE` | Start Harlequin SQL IDE for the specified database |

## 🔧 Environment Management

The tool automatically:

1. **Installs Python versions** using pyenv if not available
2. **Creates virtual environments** with naming convention `venv-odoo{VERSION}`
3. **Clones Odoo source code** to user config directory
4. **Installs system dependencies** based on your Linux distribution
5. **Installs Python dependencies** from Odoo requirements.txt


## 📋 Requirements

- **Python**: 3.10+
- **pyenv**: For Python version management
- **Git**: For cloning Odoo repositories
- **PostgreSQL**: For database operations


## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.


## 📄 License

## 🙏 Acknowledgments

- [pyenv](https://github.com/pyenv/pyenv) for Python version management
- [Harlequin](https://github.com/tconbeer/harlequin) for SQL IDE functionality

---

**Made with ❤️ for the Odoo community**
