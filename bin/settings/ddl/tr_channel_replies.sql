CREATE TABLE tr_channel_replies(
  ts TEXT PRIMARY KEY,
  thread_ts TEXT,
  reply_date TEXT,
  reply_slack_user_id TEXT,
  reply_message TEXT
)
