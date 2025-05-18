CREATE TABLE tr_channel_histories(
  ts TEXT PRIMARY KEY,
  channel_id TEXT,
  post_date TEXT,
  post_slack_user_id TEXT,
  post_message TEXT
)
