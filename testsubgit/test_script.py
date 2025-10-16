#!/usr/bin/env python3
"""
Test script for Git submodule functionality testing.
This script demonstrates that submodules can have their own code and history.
"""

import datetime
import os


def main():
    """Main function to demonstrate submodule functionality."""
    print("=== Git Submodule Test Script ===")
    print(f"Script executed at: {datetime.datetime.now()}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")

    # Check if we're running inside a submodule
    git_dir = os.path.join(os.path.dirname(__file__), '.git')
    if os.path.exists(git_dir):
        print("✓ This directory has its own .git folder")
        print("✓ This is a proper submodule with independent Git history")
    else:
        print("✗ No .git folder found in this directory")

    # Test file operations
    test_file = "submodule_test.txt"
    try:
        with open(test_file, 'w') as f:
            f.write(f"Submodule test file created at {datetime.datetime.now()}\n")
            f.write("This file is created by the submodule test script.\n")

        with open(test_file, 'r') as f:
            content = f.read()
            print(f"\nCreated and read test file content:")
            print(content)

        # Clean up
        os.remove(test_file)
        print("✓ Test file cleaned up successfully")

    except Exception as e:
        print(f"✗ Error during file operations: {e}")

    print("\n=== Test completed successfully! ===")
    print("This submodule is working correctly.")


if __name__ == "__main__":
    main()