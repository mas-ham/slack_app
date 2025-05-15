"""
dataaccess：tr_channel_histories

create 2025/05/16 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.tr_channel_histories import TrChannelHistories


TABLE_ID = 'tr_channel_histories'

class TrChannelHistoriesDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'channel_id',
            'post_date',
            'post_slack_user_id',
            'post_message',
        ]


    def select(self, conditions: list, order_by_list = None) -> list[TrChannelHistories]:
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
        return [TrChannelHistories(row['channel_id'], row['post_date'], row['post_slack_user_id'], row['post_message']) for _, row in results.iterrows()]


    def select_by_pk(self, channel_history_id) -> TrChannelHistories | None:
        """
        Select_by_PK

        Args:
            channel_history_id:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, channel_history_id = channel_history_id)
        if results.empty:
            return None
        return TrChannelHistories(results.iat[0, 0], results.iat[0, 1], results.iat[0, 2], results.iat[0, 3])


    def select_all(self, order_by_list = None) -> list[TrChannelHistories]:
        """
        Select_all

        Args:
            order_by_list:

        Returns:

        """
        results = self.execute_select_all(TABLE_ID, order_by_list)
        if results.empty:
            return []
        return [TrChannelHistories(row['channel_id'], row['post_date'], row['post_slack_user_id'], row['post_message']) for _, row in results.iterrows()]


    def insert(self, entity: TrChannelHistories) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.channel_id,
            entity.post_date,
            entity.post_slack_user_id,
            entity.post_message,
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
                    entity.channel_id,
                    entity.post_date,
                    entity.post_slack_user_id,
                    entity.post_message,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: TrChannelHistories, channel_history_id):
        """
        Update

        Args:
            entity:
            channel_history_id:

        Returns:

        """
        update_info = {
            'channel_id': entity.channel_id,
            'post_date': entity.post_date,
            'post_slack_user_id': entity.post_slack_user_id,
            'post_message': entity.post_message,
        }
        self.execute_update(TABLE_ID, update_info, channel_history_id = channel_history_id)


    def update_selective(self, entity: TrChannelHistories, channel_history_id):
        """
        Update selective

        Args:
            entity:
            channel_history_id:

        Returns:

        """
        update_info = {}
        if entity.channel_id is not None:
            update_info['channel_id'] = entity.channel_id
        if entity.post_date is not None:
            update_info['post_date'] = entity.post_date
        if entity.post_slack_user_id is not None:
            update_info['post_slack_user_id'] = entity.post_slack_user_id
        if entity.post_message is not None:
            update_info['post_message'] = entity.post_message

        self.execute_update(TABLE_ID, update_info, channel_history_id = channel_history_id)


    def delete(self, key: TrChannelHistories):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.channel_history_id is not None:
            key_map['channel_history_id'] = key.channel_history_id
        if key.channel_id is not None:
            key_map['channel_id'] = key.channel_id
        if key.post_date is not None:
            key_map['post_date'] = key.post_date
        if key.post_slack_user_id is not None:
            key_map['post_slack_user_id'] = key.post_slack_user_id
        if key.post_message is not None:
            key_map['post_message'] = key.post_message

        self.execute_delete(TABLE_ID, **key_map)


    def delete_by_pk(self, channel_history_id):
        """
        Delete_by_PK

        Args:
            channel_history_id:

        Returns:

        """
        self.execute_delete(TABLE_ID, channel_history_id = channel_history_id)


    def delete_all(self):
        """
        Delete_All

        Args:

        Returns:

        """
        self.execute_delete_all(TABLE_ID)

