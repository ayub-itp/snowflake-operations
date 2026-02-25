import os
import sys
import snowflake.connector

def log_change(env, change_file, status="SUCCESS", error_message=None):
    conn = snowflake.connector.connect(
        organization=os.getenv(f"SNOWFLAKE_ORG_{env.upper()}"),
        account=os.getenv(f"SNOWFLAKE_ACCOUNT_{env.upper()}"),
        user=os.getenv(f"SNOWFLAKE_USER_{env.upper()}"),
        role=os.getenv(f"SNOWFLAKE_ROLE_{env.upper()}"),
        authenticator=os.getenv(f"SNOWFLAKE_AUTHENTICATOR_{env.upper()}"),
        private_key=os.getenv(f"SNOWFLAKE_PRIVATE_KEY_{env.upper()}")
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO schema_change_history (environment, change_file, applied_by, status, error_message)
        VALUES (%s, %s, CURRENT_USER(), %s, %s)
    """, (env.upper(), change_file, status, error_message))
    cursor.close()
    conn.close()

if __name__ == "__main__":
    env = sys.argv[1]
    change_file = sys.argv[2]
    status = sys.argv[3] if len(sys.argv) > 3 else "SUCCESS"
    error_message = sys.argv[4] if len(sys.argv) > 4 else None
    log_change(env, change_file, status, error_message)
