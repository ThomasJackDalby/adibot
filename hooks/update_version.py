# update_version.py
# Tom Dalby

import os
import subprocess
from dataclasses import dataclass

FILE_NAME = "version.py"

def get_git_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')

@dataclass
class Version:
    major: int
    minor: int
    patch: int
    tag: str | None = None
    hash: str | None = None

def load_version(file_path) -> Version | None:
    if not os.path.exists(file_path): return None
    with open(file_path, "r") as file:
        values = [[part.strip() for part in line.strip().split("=")] for line in file.readlines()]
        parameters = { key : "=".join(value) for key, *value in values }
        
        tag = parameters.get("TAG", None)
        if tag == "None" or tag is None: tag = None
        else: tag = tag.strip("\"")

        return Version(
            major=int(parameters["MAJOR"]),
            minor=int(parameters["MINOR"]),
            patch=int(parameters["PATCH"]),
            tag=tag,
        )

def save_version(file_path: str, version: Version):
    version_str = f"v{version.major}.{version.minor}.{version.patch}"
    with open(file_path, "w") as file:
        file.write(f'''# auto-generated

MAJOR = {version.major}
MINOR = {version.minor}
PATCH = {version.patch}
TAG = {None if version.tag is None else f"\"{version.tag}\""}
VERSION = "{version_str}"
VERSION_FULL = "{version_str}{"" if version.tag is None else f"-{version.tag}"}{"" if version.hash is None else f"@{version.hash[:8]}"}"
HASH_SHORT = {None if version.hash is None else f"\"{version.hash[:8]}\"" }
HASH = {None if version.hash is None else f"\"{version.hash}\"" }
''')
        
def main():
    file_path = os.path.abspath(FILE_NAME)
    version = load_version(file_path)
    if version is None: raise Exception("Unable to load version from file.")

    # update the version
    version.hash = get_git_hash()
    version.patch += 1

    # write out the new/updated version.py
    save_version(file_path, version)

    # stage the new/updated version.py
    subprocess.call(['git', 'add', file_path])

main()