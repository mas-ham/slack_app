CREATE TABLE tr_channel_histories(
  channel_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id TEXT,
  post_date TEXT,
  post_slack_user_id TEXT,
  post_message TEXT
)
