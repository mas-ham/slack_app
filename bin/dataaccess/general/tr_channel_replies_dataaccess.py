"""
dataaccess：tr_channel_replies

create 2025/05/14 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.tr_channel_replies import TrChannelReplies


TABLE_ID = 'tr_channel_replies'

class TrChannelRepliesDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'channel_history_id',
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
        return [TrChannelReplies(row['channel_history_id'], row['reply_date'], row['reply_slack_user_id'], row['reply_message']) for _, row in results.iterrows()]


    def select_by_pk(self, channel_reply_id) -> TrChannelReplies | None:
        """
        Select_by_PK

        Args:
            channel_reply_id:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, channel_reply_id = channel_reply_id)
        if results.empty:
            return None
        return TrChannelReplies(results[0]['channel_history_id'], results[0]['reply_date'], results[0]['reply_slack_user_id'], results[0]['reply_message'])


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
        return [TrChannelReplies(row['channel_history_id'], row['reply_date'], row['reply_slack_user_id'], row['reply_message']) for _, row in results.iterrows()]


    def insert(self, entity: TrChannelReplies) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.channel_history_id,
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
                    entity.channel_history_id,
                    entity.reply_date,
                    entity.reply_slack_user_id,
                    entity.reply_message,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: TrChannelReplies, channel_reply_id):
        """
        Update

        Args:
            entity:
            channel_reply_id:

        Returns:

        """
        update_info = {
            'channel_history_id': entity.channel_history_id,
            'reply_date': entity.reply_date,
            'reply_slack_user_id': entity.reply_slack_user_id,
            'reply_message': entity.reply_message,
        }
        self.execute_update(TABLE_ID, update_info, channel_reply_id = channel_reply_id)


    def update_selective(self, entity: TrChannelReplies, channel_reply_id):
        """
        Update selective

        Args:
            entity:
            channel_reply_id:

        Returns:

        """
        update_info = {}
        if entity.channel_history_id is not None:
            update_info['channel_history_id'] = entity.channel_history_id
        if entity.reply_date is not None:
            update_info['reply_date'] = entity.reply_date
        if entity.reply_slack_user_id is not None:
            update_info['reply_slack_user_id'] = entity.reply_slack_user_id
        if entity.reply_message is not None:
            update_info['reply_message'] = entity.reply_message

        self.execute_update(TABLE_ID, update_info, channel_reply_id = channel_reply_id)


    def delete(self, key: TrChannelReplies):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.channel_reply_id is not None:
            key_map['channel_reply_id'] = key.channel_reply_id
        if key.channel_history_id is not None:
            key_map['channel_history_id'] = key.channel_history_id
        if key.reply_date is not None:
            key_map['reply_date'] = key.reply_date
        if key.reply_slack_user_id is not None:
            key_map['reply_slack_user_id'] = key.reply_slack_user_id
        if key.reply_message is not None:
            key_map['reply_message'] = key.reply_message

        self.execute_delete(TABLE_ID, **key_map)


    def delete_by_pk(self, channel_reply_id):
        """
        Delete_by_PK

        Args:
            channel_reply_id:

        Returns:

        """
        self.execute_delete(TABLE_ID, channel_reply_id = channel_reply_id)


    def delete_all(self):
        """
        Delete_All

        Args:

        Returns:

        """
        self.execute_delete(TABLE_ID)

