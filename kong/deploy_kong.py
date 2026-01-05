import os
from fabric import Connection

EC2_HOST = os.environ["EC2_HOST"]
EC2_USER = os.environ.get("EC2_USER", "ec2-user")
EC2_KEY  = os.environ["EC2_KEY_PATH"]
APP_DIR  = "/opt/kong"

def main():
    print("🔐 Connecting to EC2...")
    conn = Connection(
        host=f"{EC2_USER}@{EC2_HOST}",
        connect_kwargs={"key_filename": EC2_KEY},
    )

    print("📦 Installing Docker (safe to re-run)...")
    conn.run("sudo yum update -y", hide=False)
    conn.run("sudo yum install -y docker git", hide=False)
    conn.run("sudo systemctl start docker", hide=False)
    conn.run("sudo systemctl enable docker", hide=False)
    conn.run(f"sudo usermod -aG docker {EC2_USER}", hide=False)
    

    print("📁 Preparing /opt/kong...")
    conn.run(f"sudo mkdir -p {APP_DIR}", hide=False)
    conn.run(f"sudo chown -R {EC2_USER}:{EC2_USER} {APP_DIR}", hide=False)

    print("📤 Uploading Kong files...")
    conn.put("docker-compose.yml", f"{APP_DIR}/docker-compose.yml")
    conn.put("kong.yml", f"{APP_DIR}/kong.yml")

    print("🐳 Starting Kong...")
    conn.run(f"cd {APP_DIR} && docker compose up -d", hide=False)

    print("🎉 Kong deployed successfully")

if __name__ == "__main__":
    main()
