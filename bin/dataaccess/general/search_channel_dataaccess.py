"""
dataaccess：search_channel

create 2025/05/17 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.search_channel import SearchChannel


TABLE_ID = 'search_channel'

class SearchChannelDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'channel_id',
            'display_flg',
            'default_check_flg',
        ]


    def select(self, conditions: list, order_by_list = None) -> list[SearchChannel]:
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
        return [SearchChannel(row['channel_id'], row['display_flg'], row['default_check_flg']) for _, row in results.iterrows()]


    def select_by_pk(self, channel_id) -> SearchChannel | None:
        """
        Select_by_PK

        Args:
            channel_id:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, channel_id = channel_id)
        if results.empty:
            return None
        return SearchChannel(results.iat[0, 0], results.iat[0, 1], results.iat[0, 2])


    def select_all(self, order_by_list = None) -> list[SearchChannel]:
        """
        Select_all

        Args:
            order_by_list:

        Returns:

        """
        results = self.execute_select_all(TABLE_ID, order_by_list)
        if results.empty:
            return []
        return [SearchChannel(row['channel_id'], row['display_flg'], row['default_check_flg']) for _, row in results.iterrows()]


    def insert(self, entity: SearchChannel) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.channel_id,
            entity.display_flg,
            entity.default_check_flg,
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
                    entity.display_flg,
                    entity.default_check_flg,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: SearchChannel, channel_id):
        """
        Update

        Args:
            entity:
            channel_id:

        Returns:

        """
        update_info = {
            'channel_id': entity.channel_id,
            'display_flg': entity.display_flg,
            'default_check_flg': entity.default_check_flg,
        }
        self.execute_update(TABLE_ID, update_info, channel_id = channel_id)


    def update_selective(self, entity: SearchChannel, channel_id):
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
        if entity.display_flg is not None:
            update_info['display_flg'] = entity.display_flg
        if entity.default_check_flg is not None:
            update_info['default_check_flg'] = entity.default_check_flg

        self.execute_update(TABLE_ID, update_info, channel_id = channel_id)


    def delete(self, key: SearchChannel):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.channel_id is not None:
            key_map['channel_id'] = key.channel_id
        if key.display_flg is not None:
            key_map['display_flg'] = key.display_flg
        if key.default_check_flg is not None:
            key_map['default_check_flg'] = key.default_check_flg

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

