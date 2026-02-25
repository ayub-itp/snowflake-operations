CREATE TABLE IF NOT EXISTS ayub_history_db.ayub_history_schema.schema_change_history (
    id INT AUTOINCREMENT PRIMARY KEY,
    environment STRING NOT NULL,
    change_file STRING NOT NULL,
    applied_by STRING NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status STRING DEFAULT 'SUCCESS',
    error_message STRING
);
