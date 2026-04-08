#!/usr/bin/env /usr/bin/python
import os
import subprocess
import re
import sys

print("Running pre-commit")

commit_msg_file = sys.argv[1]
with open(commit_msg_file, 'r') as file:
    commit_msg = file.read().strip()

version_file = os.path.abspath('version.py')
hashed_code = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')

if os.path.exists(version_file):
    print(f'Reading previous {version_file}')
    with open(version_file, 'r') as f:
        content = f.read()
        major, minor, patch = map(int, re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content).groups())
    patch += 1
else:
    print(f'Creating new {version_file}')
    major, minor, patch = 0, 0, 1
print(f'Writing contents of {version_file} with "{commit_msg}"')

with open(version_file, 'w') as f:
    f.write(f'''# This file is created by the pre-push script
class Version:
    comment = "{commit_msg}"
    hash = "{hashed_code}"
    version = "{major}.{minor}.{patch}"
if __name__ == "__main__":
    print(Version.version)
''')
    
subprocess.call(['git', 'add', version_file])