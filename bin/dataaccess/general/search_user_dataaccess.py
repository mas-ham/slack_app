"""
dataaccess：search_user

create 2025/05/17 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.search_user import SearchUser


TABLE_ID = 'search_user'

class SearchUserDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'slack_user_id',
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
        return [SearchUser(row['slack_user_id'], row['display_flg'], row['default_check_flg']) for _, row in results.iterrows()]


    def select_by_pk(self, slack_user_id) -> SearchUser | None:
        """
        Select_by_PK

        Args:
            slack_user_id:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, slack_user_id = slack_user_id)
        if results.empty:
            return None
        return SearchUser(results.iat[0, 0], results.iat[0, 1], results.iat[0, 2])


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
        return [SearchUser(row['slack_user_id'], row['display_flg'], row['default_check_flg']) for _, row in results.iterrows()]


    def insert(self, entity: SearchUser) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.slack_user_id,
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
                    entity.slack_user_id,
                    entity.display_flg,
                    entity.default_check_flg,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: SearchUser, slack_user_id):
        """
        Update

        Args:
            entity:
            slack_user_id:

        Returns:

        """
        update_info = {
            'slack_user_id': entity.slack_user_id,
            'display_flg': entity.display_flg,
            'default_check_flg': entity.default_check_flg,
        }
        self.execute_update(TABLE_ID, update_info, slack_user_id = slack_user_id)


    def update_selective(self, entity: SearchUser, slack_user_id):
        """
        Update selective

        Args:
            entity:
            slack_user_id:

        Returns:

        """
        update_info = {}
        if entity.slack_user_id is not None:
            update_info['slack_user_id'] = entity.slack_user_id
        if entity.display_flg is not None:
            update_info['display_flg'] = entity.display_flg
        if entity.default_check_flg is not None:
            update_info['default_check_flg'] = entity.default_check_flg

        self.execute_update(TABLE_ID, update_info, slack_user_id = slack_user_id)


    def delete(self, key: SearchUser):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.slack_user_id is not None:
            key_map['slack_user_id'] = key.slack_user_id
        if key.display_flg is not None:
            key_map['display_flg'] = key.display_flg
        if key.default_check_flg is not None:
            key_map['default_check_flg'] = key.default_check_flg

        self.execute_delete(TABLE_ID, **key_map)


    def delete_by_pk(self, slack_user_id):
        """
        Delete_by_PK

        Args:
            slack_user_id:

        Returns:

        """
        self.execute_delete(TABLE_ID, slack_user_id = slack_user_id)


    def delete_all(self):
        """
        Delete_All

        Args:

        Returns:

        """
        self.execute_delete_all(TABLE_ID)

