import os
from fabric import Connection

EC2_HOST = os.environ["EC2_HOST"]
EC2_USER = os.environ.get("EC2_USER", "ubuntu")
EC2_KEY  = os.path.expanduser(os.environ["EC2_KEY_PATH"])
APP_DIR  = "/opt/kong"

def main():
    print("🔐 Connecting to EC2...")
    conn = Connection(
        host=f"{EC2_USER}@{EC2_HOST}",
        connect_kwargs={"key_filename": EC2_KEY},
    )

    # --------------------------------------------------
    # Check & Install Docker ONLY if missing (Ubuntu)
    # --------------------------------------------------
    print("🔍 Checking Docker installation...")
    docker_check = conn.run("command -v docker", warn=True, hide=True)

    if docker_check.failed:
        print("📦 Docker not found. Installing Docker...")
        conn.run("sudo apt update -y", hide=False)
        conn.run("sudo apt install -y docker.io docker-compose-plugin", hide=False)
        conn.run(f"sudo usermod -aG docker {EC2_USER}", hide=False)
        print("⚠️ Docker installed. A reconnect may be required.")
    else:
        print("✅ Docker already installed. Skipping install.")

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
    conn.run(f"cd {APP_DIR} && docker compose up -d", hide=False)

    print("🎉 Kong deployed successfully")

if __name__ == "__main__":
    main()
