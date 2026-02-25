import os
import sys
import snowflake.connector

def run_sql_file(conn, file_path):
    cursor = conn.cursor()
    with open(file_path, 'r') as f:
        sql = f.read()
    try:
        cursor.execute(sql)
        status = "SUCCESS"
        error_message = None
    except Exception as e:
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

    conn = snowflake.connector.connect(
        organization=os.getenv(f"SNOWFLAKE_ORG_{env.upper()}"),
        account=os.getenv(f"SNOWFLAKE_ACCOUNT_{env.upper()}"),
        user=os.getenv(f"SNOWFLAKE_USER_{env.upper()}"),
        role=os.getenv(f"SNOWFLAKE_ROLE_{env.upper()}"),
        authenticator=os.getenv(f"SNOWFLAKE_AUTHENTICATOR_{env.upper()}"),
        private_key=os.getenv(f"SNOWFLAKE_PRIVATE_KEY_{env.upper()}")
    )

    for file in sorted(os.listdir(changes_dir)):
        if file.endswith(".sql"):
            run_sql_file(conn, os.path.join(changes_dir, file))

    conn.close()
