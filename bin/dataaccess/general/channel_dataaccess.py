"""
dataaccess：channel

create 2025/05/16 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.channel import Channel


TABLE_ID = 'channel'

class ChannelDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'channel_id',
            'channel_name',
            'channel_type',
        ]


    def select(self, conditions: list, order_by_list = None) -> list[Channel]:
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
        return [Channel(row['channel_id'], row['channel_name'], row['channel_type']) for _, row in results.iterrows()]


    def select_by_pk(self, channel_id) -> Channel | None:
        """
        Select_by_PK

        Args:
            channel_id:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, channel_id = channel_id)
        if results.empty:
            return None
        return Channel(results.iat[0, 0], results.iat[0, 1], results.iat[0, 2])


    def select_all(self, order_by_list = None) -> list[Channel]:
        """
        Select_all

        Args:
            order_by_list:

        Returns:

        """
        results = self.execute_select_all(TABLE_ID, order_by_list)
        if results.empty:
            return []
        return [Channel(row['channel_id'], row['channel_name'], row['channel_type']) for _, row in results.iterrows()]


    def insert(self, entity: Channel) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.channel_id,
            entity.channel_name,
            entity.channel_type,
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
                    entity.channel_name,
                    entity.channel_type,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: Channel, channel_id):
        """
        Update

        Args:
            entity:
            channel_id:

        Returns:

        """
        update_info = {
            'channel_id': entity.channel_id,
            'channel_name': entity.channel_name,
            'channel_type': entity.channel_type,
        }
        self.execute_update(TABLE_ID, update_info, channel_id = channel_id)


    def update_selective(self, entity: Channel, channel_id):
        """
        Update selective

        Args:
            entity:
            channel_id:

        Returns:

        """
        update_info = {}
        if entity.channel_id is not None:
            update_info['channel_id'] = entity.channel_id
        if entity.channel_name is not None:
            update_info['channel_name'] = entity.channel_name
        if entity.channel_type is not None:
            update_info['channel_type'] = entity.channel_type

        self.execute_update(TABLE_ID, update_info, channel_id = channel_id)


    def delete(self, key: Channel):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.channel_id is not None:
            key_map['channel_id'] = key.channel_id
        if key.channel_name is not None:
            key_map['channel_name'] = key.channel_name
        if key.channel_type is not None:
            key_map['channel_type'] = key.channel_type

        self.execute_delete(TABLE_ID, **key_map)


    def delete_by_pk(self, channel_id):
        """
        Delete_by_PK

        Args:
            channel_id:

        Returns:

        """
        self.execute_delete(TABLE_ID, channel_id = channel_id)


    def delete_all(self):
        """
        Delete_All

        Args:

        Returns:

        """
        self.execute_delete_all(TABLE_ID)

