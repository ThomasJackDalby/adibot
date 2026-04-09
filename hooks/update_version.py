# update_version.py
# Tom Dalby

import os
import subprocess
import re
import sys
import json
from dataclasses import dataclass
import logging

logger = logging.getLogger(__file__)

FILE_NAME = "version.py"

def get_git_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')

@dataclass
class Version:
    major: int
    minor: int
    patch: int
    tag: str
    hash: str

def load_version(file_path) -> Version | None:
    print(file_path)
    if not os.path.exists(file_path): return None
    with open(file_path, "r") as file:
        values = [[part.strip() for part in line.strip().split("=")] for line in file.readlines()]
        parameters = { key : value for key, *value in values }
        print(parameters)

# def write(file_path, version: Version):

#     version = f"{major}.{minor}.{patch}"

#     with open(file_path, 'w') as f:
#         f.write(f'''# auto-generated

# VERSION = {}            
# MAJOR = {major}
# MINOR = {minor}
# PATCH = {patch}
# SUFFIX = {}

# ''')
        
def main():
    print("running main")
    file_path = os.path.abspath(FILE_NAME)
    version = load_version(file_path)

    # hashed_code = get_git_hash()


    # write(file_path, major, minor, patch, hashed_code)
    # subprocess.call(['git', 'add', file_path])

logger.info("got to here")
main()