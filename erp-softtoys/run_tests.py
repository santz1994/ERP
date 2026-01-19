#!/usr/bin/env python
"""
Quick Test Runner for Phase 1 Authentication
Run all tests with verbose output and coverage

Usage:
    python run_tests.py                    # All tests
    python run_tests.py auth               # Auth tests only
    python run_tests.py admin              # Admin tests only
    python run_tests.py --verbose          # Extra verbose
    python run_tests.py --coverage         # With coverage report
"""

import subprocess
import sys
import os


def run_tests(test_filter=None, verbose=False, coverage=False):
    """Run pytest with specified options"""
    
    cmd = ["pytest", "tests/"]
    
    # Add test filter if specified
    if test_filter:
        if test_filter == "auth":
            cmd.append("test_auth.py")
        elif test_filter == "admin":
            cmd.append("test_auth.py::TestAdminEndpoints")
    
    # Add flags
    if verbose:
        cmd.append("-vv")  # Extra verbose
    else:
        cmd.append("-v")   # Verbose
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add extra options
    cmd.extend([
        "--tb=short",           # Shorter traceback format
        "--strict-markers",     # Strict marker checking
        "-ra",                  # Show summary of all outcomes
    ])
    
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__) or ".")
    return result.returncode


if __name__ == "__main__":
    # Parse arguments
    test_filter = None
    verbose = False
    coverage = False
    
    for arg in sys.argv[1:]:
        if arg in ["auth", "admin"]:
            test_filter = arg
        elif arg == "--verbose":
            verbose = True
        elif arg == "--coverage":
            coverage = True
        elif arg == "-h" or arg == "--help":
            print(__doc__)
            sys.exit(0)
    
    # Run tests
    exit_code = run_tests(
        test_filter=test_filter,
        verbose=verbose,
        coverage=coverage
    )
    
    sys.exit(exit_code)
