#!/usr/bin/env python3


import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(
    test_path=None, verbose=False, coverage=False, parallel=False, markers=None
):
    """
    Run tests with specified options.

    Args:
        test_path: Specific test file or directory to run
        verbose: Enable verbose output
        coverage: Run with coverage reporting
        parallel: Run tests in parallel
        markers: Run only tests with specific markers
    """
    cmd = [sys.executable, "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=run_odoo", "--cov-report=term-missing", "--cov-report=html"])

    if parallel:
        cmd.extend(["-n", "auto"])

    if markers:
        cmd.extend(["-m", markers])

    if test_path:
        cmd.append(str(test_path))
    else:
        # Run all tests in the tests directory
        cmd.append("tests/")

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        return e.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for run-odoo package")
    parser.add_argument(
        "test_path",
        nargs="?",
        help="Specific test file or directory to run (default: all tests)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Run with coverage reporting"
    )
    parser.add_argument(
        "-p", "--parallel", action="store_true", help="Run tests in parallel"
    )
    parser.add_argument(
        "-m",
        "--markers",
        help="Run only tests with specific markers (e.g., 'slow', 'integration')",
    )
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="List all available tests without running them",
    )
    parser.add_argument(
        "--list-markers", action="store_true", help="List all available markers"
    )

    args = parser.parse_args()

    # Change to the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    if args.list_tests:
        cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
        if args.test_path:
            cmd.append(str(args.test_path))
        else:
            cmd.append("tests/")
        subprocess.run(cmd)
        return 0

    if args.list_markers:
        cmd = [sys.executable, "-m", "pytest", "--markers"]
        subprocess.run(cmd)
        return 0

    return run_tests(
        test_path=args.test_path,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel,
        markers=args.markers,
    )


if __name__ == "__main__":
    import os

    exit_code = main()
    sys.exit(exit_code)

