from datetime import date
import argparse
import subprocess

def get_nightly_version():
    today = date.today()
    return today.strftime("%Y.%m.%d")

if __name__ == "__main__":

    def try_and_handle(cmd, dry_run = False):
        if dry_run:
            print(f"Executing command: {cmd}")
        else:
            try:
                subprocess.run([cmd], shell=True, check = True)
            except subprocess.CalledProcessError as e:
                raise(e)
    
    failed_commands = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--organization", type=str, default="pytorch", help="The name of the Dockerhub organization where the images will be pushed")
    parser.add_argument("--dry_run", action="store_true", help="dry_run will print the commands that will be run without running them")
    args = parser.parse_args()
    dry_run = args.dry_run
    organization = args.organization
    
    project = "torchserve-nightly"
    cpu_version = f"{project}:cpu-{get_nightly_version()}"
    gpu_version = f"{project}:gpu-{get_nightly_version()}"

    # Build Nightly images and append the date in the name
    try_and_handle(f"./build_image.sh -bt dev -t {organization}/{cpu_version}", dry_run)
    try_and_handle(f"./build_image.sh -bt dev -g -cv cu102 -t {organization}/{gpu_version}", dry_run)

    # Push Nightly images to official PyTorch Dockerhub account
    try_and_handle(f"docker push {organization}/{cpu_version}", dry_run)
    try_and_handle(f"docker push {organization}/{gpu_version}", dry_run)

    
    # Tag nightly images with latest
    try_and_handle(f"docker tag {organization}/{cpu_version} {organization}/{project}:latest-cpu", dry_run)
    try_and_handle(f"docker tag {organization}/{gpu_version} {organization}/{project}:latest-gpu", dry_run)

    # Push images with latest tag
    try_and_handle(f"docker push {organization}/{project}:latest-cpu", dry_run)
    try_and_handle(f"docker push {organization}/{project}:latest-gpu", dry_run)
