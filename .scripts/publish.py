import subprocess
import argparse

GITEA_URL = "192.168.0.100:3000"
GITEA_USERNAME = "dalby"
DOCKER_IMAGES = [
    ["adibot", "adibot"],
]
VERSION = "v0.1.1-beta"

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