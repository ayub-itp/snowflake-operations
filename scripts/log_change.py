import os
import sys
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def load_private_key(env_key):
    pem_str = os.getenv(f"SNOWFLAKE_PRIVATE_KEY_{env_key}")
    if not pem_str:
        raise ValueError("Private key not set in environment")
    pem_bytes = pem_str.encode("utf-8")
    private_key = serialization.load_pem_private_key(
        pem_bytes,
        password=None,
        backend=default_backend()
    )
    return private_key

def run_sql_file(conn, env_key, file_path):
    cursor = conn.cursor()
    with open(file_path, 'r') as f:
        sql = f.read()
    try:
        print(f"Applying {file_path}...")
        cursor.execute(sql)
        status = "SUCCESS"
        error_message = None
    except Exception as e:
        print(f"Error applying {file_path}: {e}")
        status = "FAILED"
        error_message = str(e)
    finally:
        cursor.execute(f"""
            INSERT INTO ayub_github_audit_db.ayub_github_schema_db.schema_change_history
            (environment, change_file, applied_by, status, error_message)
            VALUES (%s, %s, CURRENT_USER(), %s, %s)
        """, (env_key, os.path.basename(file_path), status, error_message))
        cursor.close()

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

    # Apply all SQL files in changes/<env>/
    changes_dir = f"changes/{env}/"
    for file in sorted(os.listdir(changes_dir)):
        if file.endswith(".sql"):
            run_sql_file(conn, env_key, os.path.join(changes_dir, file))

    conn.close()
    print("✅ All migrations applied and logged.")
