import os
import sys
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def load_private_key(env_key):
    pem_str = os.getenv(f"SNOWFLAKE_PRIVATE_KEY_{env_key}")
    if not pem_str:
        raise ValueError("Private key not set in environment")
    # Convert string to bytes
    pem_bytes = pem_str.encode("utf-8")
    # Load RSA key object
    private_key = serialization.load_pem_private_key(
        pem_bytes,
        password=None,
        backend=default_backend()
    )
    return private_key

if __name__ == "__main__":
    env = sys.argv[1].lower()
    env_map = {"dev": "DEV", "qa": "QA", "prod": "PROD"}
    env_key = env_map.get(env)

    private_key = load_private_key(env_key)

    conn = snowflake.connector.connect(
        organization=os.getenv(f"SNOWFLAKE_ORG_{env_key}"),
        account=os.getenv(f"SNOWFLAKE_ACCOUNT_{env_key}"),
        user=os.getenv(f"SNOWFLAKE_USER_{env_key}"),
        role=os.getenv(f"SNOWFLAKE_ROLE_{env_key}"),
        authenticator=os.getenv(f"SNOWFLAKE_AUTHENTICATOR_{env_key}"),
        private_key=private_key
    )
    print("✅ Connection established successfully.")
