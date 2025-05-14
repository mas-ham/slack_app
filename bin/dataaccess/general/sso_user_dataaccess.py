"""
dataaccess：sso_user

create 2025/05/14 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.sso_user import SsoUser


TABLE_ID = 'sso_user'

class SsoUserDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'pc_user',
            'user_id',
            'is_admin',
        ]


    def select(self, conditions: list, order_by_list = None) -> list[SsoUser]:
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
        return [SsoUser(row['pc_user'], row['user_id'], row['is_admin']) for _, row in results.iterrows()]


    def select_by_pk(self, pc_user) -> SsoUser | None:
        """
        Select_by_PK

        Args:
            pc_user:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, pc_user = pc_user)
        if results.empty:
            return None
        return SsoUser(results[0]['pc_user'], results[0]['user_id'], results[0]['is_admin'])


    def select_all(self, order_by_list = None) -> list[SsoUser]:
        """
        Select_all

        Args:
            order_by_list:

        Returns:

        """
        results = self.execute_select_all(TABLE_ID, order_by_list)
        if results.empty:
            return []
        return [SsoUser(row['pc_user'], row['user_id'], row['is_admin']) for _, row in results.iterrows()]


    def insert(self, entity: SsoUser) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.pc_user,
            entity.user_id,
            entity.is_admin,
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
                    entity.pc_user,
                    entity.user_id,
                    entity.is_admin,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: SsoUser, pc_user):
        """
        Update

        Args:
            entity:
            pc_user:

        Returns:

        """
        update_info = {
            'pc_user': entity.pc_user,
            'user_id': entity.user_id,
            'is_admin': entity.is_admin,
        }
        self.execute_update(TABLE_ID, update_info, pc_user = pc_user)


    def update_selective(self, entity: SsoUser, pc_user):
        """
        Update selective

        Args:
            entity:
            pc_user:

        Returns:

        """
        update_info = {}
        if entity.pc_user is not None:
            update_info['pc_user'] = entity.pc_user
        if entity.user_id is not None:
            update_info['user_id'] = entity.user_id
        if entity.is_admin is not None:
            update_info['is_admin'] = entity.is_admin

        self.execute_update(TABLE_ID, update_info, pc_user = pc_user)


    def delete(self, key: SsoUser):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.pc_user is not None:
            key_map['pc_user'] = key.pc_user
        if key.user_id is not None:
            key_map['user_id'] = key.user_id
        if key.is_admin is not None:
            key_map['is_admin'] = key.is_admin

        self.execute_delete(TABLE_ID, **key_map)


    def delete_by_pk(self, pc_user):
        """
        Delete_by_PK

        Args:
            pc_user:

        Returns:

        """
        self.execute_delete(TABLE_ID, pc_user = pc_user)


    def delete_all(self):
        """
        Delete_All

        Args:

        Returns:

        """
        self.execute_delete(TABLE_ID)

