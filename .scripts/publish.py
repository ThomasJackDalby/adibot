import subprocess
import argparse

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from version import VERSION

GITEA_URL = "192.168.0.100:3000"
GITEA_USERNAME = "dalby"
DOCKER_IMAGES = [
    ["adibot", "adibot"],
]

def main(args):
    for image_name, docker_target in DOCKER_IMAGES:
        docker_tag = f"{GITEA_URL}/{GITEA_USERNAME}/{image_name}"
        subprocess.run(f"docker build -t {docker_tag}:{VERSION} --target {docker_target} .")
        subprocess.run(f"docker push {docker_tag}:{VERSION}")
        
        subprocess.run(f"docker image tag {docker_tag}:{VERSION} {docker_tag}:latest")
        subprocess.run(f"docker push {docker_tag}:latest")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    main(vars(parser.parse_args()))