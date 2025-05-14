CREATE TABLE search_channel(
  settings_user_id TEXT,
  channel_id TEXT,
  display_flg INTEGER,
  default_check_flg INTEGER,
  PRIMARY KEY(settings_user_id, channel_id)
)
