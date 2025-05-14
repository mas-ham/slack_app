CREATE TABLE search_user(
  settings_user_id TEXT,
  slack_user_id TEXT,
  display_flg INTEGER,
  default_check_flg INTEGER,
  PRIMARY KEY(settings_user_id, slack_user_id)
)
