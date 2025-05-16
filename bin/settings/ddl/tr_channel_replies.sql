CREATE TABLE tr_channel_replies(
  channel_reply_id INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_history_id,
  reply_date TEXT UNIQUE,
  reply_slack_user_id TEXT,
  reply_message TEXT
)
