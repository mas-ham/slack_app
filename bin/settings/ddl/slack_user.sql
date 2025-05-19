CREATE TABLE IF NOT EXISTS slack_user(
  slack_user_id TEXT PRIMARY KEY,
  user_id TEXT,
  user_name TEXT,
  icon TEXT,
  delete_flg INTEGER
)
