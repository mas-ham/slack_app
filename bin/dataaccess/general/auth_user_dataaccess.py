"""
dataaccess：auth_user

create 2025/05/14 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.auth_user import AuthUser


TABLE_ID = 'auth_user'

class AuthUserDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'user_id',
            'channel_id',
        ]


    def select(self, conditions: list, order_by_list = None) -> list[AuthUser]:
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
        return [AuthUser(row['user_id'], row['channel_id']) for _, row in results.iterrows()]


    def select_by_pk(self, user_id) -> AuthUser | None:
        """
        Select_by_PK

        Args:
            user_id:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, user_id = user_id)
        if results.empty:
            return None
        return AuthUser(results[0]['user_id'], results[0]['channel_id'])


    def select_all(self, order_by_list = None) -> list[AuthUser]:
        """
        Select_all

        Args:
            order_by_list:

        Returns:

        """
        results = self.execute_select_all(TABLE_ID, order_by_list)
        if results.empty:
            return []
        return [AuthUser(row['user_id'], row['channel_id']) for _, row in results.iterrows()]


    def insert(self, entity: AuthUser) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.user_id,
            entity.channel_id,
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
                    entity.user_id,
                    entity.channel_id,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: AuthUser, user_id):
        """
        Update

        Args:
            entity:
            user_id:

        Returns:

        """
        update_info = {
            'user_id': entity.user_id,
            'channel_id': entity.channel_id,
        }
        self.execute_update(TABLE_ID, update_info, user_id = user_id)


    def update_selective(self, entity: AuthUser, user_id):
        """
        Update selective

        Args:
            entity:
            user_id:

        Returns:

        """
        update_info = {}
        if entity.user_id is not None:
            update_info['user_id'] = entity.user_id
        if entity.channel_id is not None:
            update_info['channel_id'] = entity.channel_id

        self.execute_update(TABLE_ID, update_info, user_id = user_id)


    def delete(self, key: AuthUser):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.user_id is not None:
            key_map['user_id'] = key.user_id
        if key.channel_id is not None:
            key_map['channel_id'] = key.channel_id

        self.execute_delete(TABLE_ID, **key_map)


    def delete_by_pk(self, user_id):
        """
        Delete_by_PK

        Args:
            user_id:

        Returns:

        """
        self.execute_delete(TABLE_ID, user_id = user_id)


    def delete_all(self):
        """
        Delete_All

        Args:

        Returns:

        """
        self.execute_delete(TABLE_ID)

