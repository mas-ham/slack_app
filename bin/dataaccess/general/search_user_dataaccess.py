"""
dataaccess：search_user

create 2025/05/13 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.search_user import SearchUser


TABLE_ID = 'search_user'

class SearchUserDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'settings_user_id',
            'user_id',
            'display_flg',
            'default_check_flg',
        ]


    def select(self, conditions: list, order_by_list = None) -> list[SearchUser]:
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
        return [SearchUser(row['settings_user_id'], row['user_id'], row['display_flg'], row['default_check_flg']) for _, row in results.iterrows()]


    def select_by_pk(self, ) -> SearchUser | None:
        """
        Select_by_PK

        Args:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, )
        if results.empty:
            return None
        return SearchUser(results[0]['settings_user_id'], results[0]['user_id'], results[0]['display_flg'], results[0]['default_check_flg'])


    def select_all(self, order_by_list = None) -> list[SearchUser]:
        """
        Select_all

        Args:
            order_by_list:

        Returns:

        """
        results = self.execute_select_all(TABLE_ID, order_by_list)
        if results.empty:
            return []
        return [SearchUser(row['settings_user_id'], row['user_id'], row['display_flg'], row['default_check_flg']) for _, row in results.iterrows()]


    def insert(self, entity: SearchUser) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.settings_user_id,
            entity.user_id,
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
                    entity.settings_user_id,
                    entity.user_id,
                    entity.display_flg,
                    entity.default_check_flg,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: SearchUser, ):
        """
        Update

        Args:
            entity:

        Returns:

        """
        update_info = {
            'settings_user_id': entity.settings_user_id,
            'user_id': entity.user_id,
            'display_flg': entity.display_flg,
            'default_check_flg': entity.default_check_flg,
        }
        self.execute_update(TABLE_ID, update_info, )


    def update_selective(self, entity: SearchUser, ):
        """
        Update selective

        Args:
            entity:

        Returns:

        """
        update_info = {}
        if entity.settings_user_id is not None:
            update_info['settings_user_id'] = entity.settings_user_id
        if entity.user_id is not None:
            update_info['user_id'] = entity.user_id
        if entity.display_flg is not None:
            update_info['display_flg'] = entity.display_flg
        if entity.default_check_flg is not None:
            update_info['default_check_flg'] = entity.default_check_flg

        self.execute_update(TABLE_ID, update_info, )


    def delete(self, key: SearchUser):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.settings_user_id is not None:
            key_map['settings_user_id'] = key.settings_user_id
        if key.user_id is not None:
            key_map['user_id'] = key.user_id
        if key.display_flg is not None:
            key_map['display_flg'] = key.display_flg
        if key.default_check_flg is not None:
            key_map['default_check_flg'] = key.default_check_flg

        self.execute_delete(TABLE_ID, **key_map)


    def delete_by_pk(self, ):
        """
        Delete_by_PK

        Args:

        Returns:

        """
        self.execute_delete(TABLE_ID, )

