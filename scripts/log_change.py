import os
import sys
import snowflake.connector

def debug_env(env):
    """Print out the key environment variables for debugging."""
    keys = [
        f"SNOWFLAKE_ORG_{env.upper()}",
        f"SNOWFLAKE_ACCOUNT_{env.upper()}",
        f"SNOWFLAKE_USER_{env.upper()}",
        f"SNOWFLAKE_ROLE_{env.upper()}",
        f"SNOWFLAKE_AUTHENTICATOR_{env.upper()}",
        f"SNOWFLAKE_PRIVATE_KEY_{env.upper()}"
    ]
    print("=== Debugging Environment Variables ===")
    for k in keys:
        v = os.getenv(k)
        if v:
            # Mask sensitive values like private key
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
    env = sys.argv[1]
    changes_dir = f"changes/{env}/"

    # Debug print environment variables
    debug_env(env)

    # Attempt connection
    try:
        conn = snowflake.connector.connect(
            organization=os.getenv(f"SNOWFLAKE_ORG_{env.upper()}"),
            account=os.getenv(f"SNOWFLAKE_ACCOUNT_{env.upper()}"),
            user=os.getenv(f"SNOWFLAKE_USER_{env.upper()}"),
            role=os.getenv(f"SNOWFLAKE_ROLE_{env.upper()}"),
            authenticator=os.getenv(f"SNOWFLAKE_AUTHENTICATOR_{env.upper()}"),
            private_key=os.getenv(f"SNOWFLAKE_PRIVATE_KEY_{env.upper()}")
        )
        print("✅ Connection established successfully.")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

    # Apply SQL files
    for file in sorted(os.listdir(changes_dir)):
        if file.endswith(".sql"):
            run_sql_file(conn, env, os.path.join(changes_dir, file))

    conn.close()
    print("✅ All migrations applied and logged.")
