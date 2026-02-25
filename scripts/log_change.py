import os
import sys
import snowflake.connector

def debug_env(env_key):
    keys = [
        f"SNOWFLAKE_ORG_{env_key}",
        f"SNOWFLAKE_ACCOUNT_{env_key}",
        f"SNOWFLAKE_USER_{env_key}",
        f"SNOWFLAKE_ROLE_{env_key}",
        f"SNOWFLAKE_AUTHENTICATOR_{env_key}",
        f"SNOWFLAKE_PRIVATE_KEY_{env_key}"
    ]
    print("=== Debugging Environment Variables ===")
    for k in keys:
        v = os.getenv(k)
        if v:
            masked = v if "PRIVATE_KEY" not in k else "[PRIVATE_KEY_SET]"
            print(f"{k}: {masked}")
        else:
            print(f"{k}: NOT SET")
    print("=======================================")

def run_sql_file(conn, env, file_path):
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
        cursor.execute("""
            INSERT INTO schema_change_history (environment, change_file, applied_by, status, error_message)
            VALUES (%s, %s, CURRENT_USER(), %s, %s)
        """, (env.upper(), os.path.basename(file_path), status, error_message))
        cursor.close()

if __name__ == "__main__":
    env = sys.argv[1].lower()
    env_map = {"dev": "DEV", "qa": "QA", "prod": "PROD"}
    env_key = env_map.get(env)

    if not env_key:
        print(f"❌ Unknown environment: {env}")
        sys.exit(1)

    changes_dir = f"changes/{env}/"

    debug_env(env_key)

    try:
        conn = snowflake.connector.connect(
            organization=os.getenv(f"SNOWFLAKE_ORG_{env_key}"),
            account=os.getenv(f"SNOWFLAKE_ACCOUNT_{env_key}"),
            user=os.getenv(f"SNOWFLAKE_USER_{env_key}"),
            role=os.getenv(f"SNOWFLAKE_ROLE_{env_key}"),
            authenticator=os.getenv(f"SNOWFLAKE_AUTHENTICATOR_{env_key}"),
            private_key=os.getenv(f"SNOWFLAKE_PRIVATE_KEY_{env_key}")
        )
        print("✅ Connection established successfully.")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

    for file in sorted(os.listdir(changes_dir)):
        if file.endswith(".sql"):
            run_sql_file(conn, env_key, os.path.join(changes_dir, file))

    conn.close()
    print("✅ All migrations applied and logged.")
