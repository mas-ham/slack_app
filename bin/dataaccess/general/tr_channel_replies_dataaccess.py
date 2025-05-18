"""
dataaccess：tr_channel_replies

create 2025/05/18 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.tr_channel_replies import TrChannelReplies


TABLE_ID = 'tr_channel_replies'

class TrChannelRepliesDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'ts',
            'thread_ts',
            'reply_date',
            'reply_slack_user_id',
            'reply_message',
        ]


    def select(self, conditions: list, order_by_list = None) -> list[TrChannelReplies]:
        """
        Select

        Args:
            conditions:
            order_by_list:

        Returns:

        """

        results = self.execute_select(TABLE_ID, conditions, order_by_list)
        if results.empty:
            return []
        return [TrChannelReplies(row['ts'], row['thread_ts'], row['reply_date'], row['reply_slack_user_id'], row['reply_message']) for _, row in results.iterrows()]


    def select_by_pk(self, ts) -> TrChannelReplies | None:
        """
        Select_by_PK

        Args:
            ts:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, ts = ts)
        if results.empty:
            return None
        return TrChannelReplies(results.iat[0, 0], results.iat[0, 1], results.iat[0, 2], results.iat[0, 3], results.iat[0, 4])


    def select_all(self, order_by_list = None) -> list[TrChannelReplies]:
        """
        Select_all

        Args:
            order_by_list:

        Returns:

        """
        results = self.execute_select_all(TABLE_ID, order_by_list)
        if results.empty:
            return []
        return [TrChannelReplies(row['ts'], row['thread_ts'], row['reply_date'], row['reply_slack_user_id'], row['reply_message']) for _, row in results.iterrows()]


    def insert(self, entity: TrChannelReplies) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.ts,
            entity.thread_ts,
            entity.reply_date,
            entity.reply_slack_user_id,
            entity.reply_message,
        )
        return self.execute_insert(TABLE_ID, self.col_list, params)


    def insert_many(self, entity_list: list):
        """
        Insert_many

        Args:
            entity_list:

        Returns:

        """
        params = []
        for entity in entity_list:
            params.append(
                (
                    entity.ts,
                    entity.thread_ts,
                    entity.reply_date,
                    entity.reply_slack_user_id,
                    entity.reply_message,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: TrChannelReplies, ts):
        """
        Update

        Args:
            entity:
            ts:

        Returns:

        """
        update_info = {
            'ts': entity.ts,
            'thread_ts': entity.thread_ts,
            'reply_date': entity.reply_date,
            'reply_slack_user_id': entity.reply_slack_user_id,
            'reply_message': entity.reply_message,
        }
        self.execute_update(TABLE_ID, update_info, ts = ts)


    def update_selective(self, entity: TrChannelReplies, ts):
        """
        Update selective

        Args:
            entity:
            ts:

        Returns:

        """
        update_info = {}
        if entity.ts is not None:
            update_info['ts'] = entity.ts
        if entity.thread_ts is not None:
            update_info['thread_ts'] = entity.thread_ts
        if entity.reply_date is not None:
            update_info['reply_date'] = entity.reply_date
        if entity.reply_slack_user_id is not None:
            update_info['reply_slack_user_id'] = entity.reply_slack_user_id
        if entity.reply_message is not None:
            update_info['reply_message'] = entity.reply_message

        self.execute_update(TABLE_ID, update_info, ts = ts)


    def delete(self, key: TrChannelReplies):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.ts is not None:
            key_map['ts'] = key.ts
        if key.thread_ts is not None:
            key_map['thread_ts'] = key.thread_ts
        if key.reply_date is not None:
            key_map['reply_date'] = key.reply_date
        if key.reply_slack_user_id is not None:
            key_map['reply_slack_user_id'] = key.reply_slack_user_id
        if key.reply_message is not None:
            key_map['reply_message'] = key.reply_message

        self.execute_delete(TABLE_ID, **key_map)


    def delete_by_pk(self, ts):
        """
        Delete_by_PK

        Args:
            ts:

        Returns:

        """
        self.execute_delete(TABLE_ID, ts = ts)


    def delete_all(self):
        """
        Delete_All

        Args:

        Returns:

        """
        self.execute_delete_all(TABLE_ID)

