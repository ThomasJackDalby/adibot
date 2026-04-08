#!/usr/bin/env /usr/bin/python
import os
import subprocess
import re
import sys

FILE_NAME = "version.py"

def get_git_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')

def get_current_version(file_path) -> tuple[int, int, int, str | None]:
    if os.path.exists(file_path):
        print(f'Reading previous {file_path}')
        with open(file_path, 'r') as f:
            content = f.read()
            major, minor, patch = map(int, re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content).groups())
        patch += 1
    else:
        print(f'Creating new {file_path}')
        major, minor, patch = 0, 0, 1
    return major, minor, patch, None

def write(file_path, major, minor, patch, suffix, hashed_code):
    with open(file_path, 'w') as f:
        f.write(f'''# auto-generated
                
    class Version:
        hash = "{hashed_code}"
        version = "{major}.{minor}.{patch}"

    if __name__ == "__main__":
        print(Version.version)
    ''')
        
def main():
    file_path = os.path.abspath(FILE_NAME)
    major, minor, patch, suffix = get_current_version(file_path)
    hashed_code = get_git_hash()
    write(file_path, major, minor, patch, suffix, hashed_code)
    subprocess.call(['git', 'add', file_path])