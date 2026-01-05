import os
import sys
from fabric import Connection
from invoke import UnexpectedExit

EC2_HOST = os.environ["EC2_HOST"]
EC2_USER = os.environ.get("EC2_USER", "ubuntu")
EC2_KEY  = os.path.expanduser(os.environ["EC2_KEY_PATH"])
APP_DIR  = "/opt/kong"

def main():
    print("🔐 Connecting to EC2...")
    try:
        conn = Connection(
            host=f"{EC2_USER}@{EC2_HOST}",
            connect_kwargs={"key_filename": EC2_KEY},
        )

        # --------------------------------------------------
            # Check & Install Docker 
            # --------------------------------------------------
        print("🔍 Checking Docker installation...")
        docker_check = conn.run("command -v docker", warn=True, hide=True)

        if docker_check.failed:
            print("📦 Docker not found. Installing via official script...")
            # Using the official script ensures  get the 'docker compose' plugin
            conn.run("curl -fsSL https://get.docker.com | sh", hide=False)
            
            # Still add user to group for future manual SSH access
            conn.run(f"sudo usermod -aG docker {EC2_USER}", hide=False)
            print(".........Docker installed successfully.")
        else:
            print("......Docker is already installed.")

        # --------------------------------------------------
        # Prepare application directory
        # --------------------------------------------------
        print("📁 Preparing /opt/kong...")
        conn.run(f"sudo mkdir -p {APP_DIR}", hide=False)
        conn.run(f"sudo chown -R {EC2_USER}:{EC2_USER} {APP_DIR}", hide=False)

        # --------------------------------------------------
        # Upload Kong config
        # --------------------------------------------------
        print("📤 Uploading Kong files...")
        conn.put("docker-compose.yml", f"{APP_DIR}/docker-compose.yml")
        conn.put("kong.yml", f"{APP_DIR}/kong.yml")

        # --------------------------------------------------
        # Start Kong
        # --------------------------------------------------
        print("🐳 Starting Kong...")
        conn.run(f"cd {APP_DIR} && sudo docker compose up -d", hide=False)

        print("🎉 Kong deployed successfully")
    except UnexpectedExit as e:
        print(f"\n❌ Remote command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
