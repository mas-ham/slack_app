"""
dataaccess：slack_user

create 2025/05/16 hamada
"""
from dataaccess.common.base_dataaccess import BaseDataAccess
from dataaccess.entity.slack_user import SlackUser


TABLE_ID = 'slack_user'

class SlackUserDataAccess(BaseDataAccess):
    def __init__(self, conn):
        super().__init__(conn)

        self.col_list = [
            'slack_user_id',
            'user_id',
            'user_name',
            'icon',
            'delete_flg',
        ]


    def select(self, conditions: list, order_by_list = None) -> list[SlackUser]:
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
        return [SlackUser(row['slack_user_id'], row['user_id'], row['user_name'], row['icon'], row['delete_flg']) for _, row in results.iterrows()]


    def select_by_pk(self, slack_user_id) -> SlackUser | None:
        """
        Select_by_PK

        Args:
            slack_user_id:

        Returns:

        """
        results = self.execute_select_by_pk(TABLE_ID, slack_user_id = slack_user_id)
        if results.empty:
            return None
        return SlackUser(results.iat[0, 0], results.iat[0, 1], results.iat[0, 2], results.iat[0, 3], results.iat[0, 4])


    def select_all(self, order_by_list = None) -> list[SlackUser]:
        """
        Select_all

        Args:
            order_by_list:

        Returns:

        """
        results = self.execute_select_all(TABLE_ID, order_by_list)
        if results.empty:
            return []
        return [SlackUser(row['slack_user_id'], row['user_id'], row['user_name'], row['icon'], row['delete_flg']) for _, row in results.iterrows()]


    def insert(self, entity: SlackUser) -> int:
        """
        Insert

        Args:
            entity:

        Returns:

        """
        params = (
            entity.slack_user_id,
            entity.user_id,
            entity.user_name,
            entity.icon,
            entity.delete_flg,
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
                    entity.user_id,
                    entity.user_name,
                    entity.icon,
                    entity.delete_flg,
                )
            )
        self.execute_insert_many(TABLE_ID, self.col_list, params)


    def update(self, entity: SlackUser, slack_user_id):
        """
        Update

        Args:
            entity:
            slack_user_id:

        Returns:

        """
        update_info = {
            'slack_user_id': entity.slack_user_id,
            'user_id': entity.user_id,
            'user_name': entity.user_name,
            'icon': entity.icon,
            'delete_flg': entity.delete_flg,
        }
        self.execute_update(TABLE_ID, update_info, slack_user_id = slack_user_id)


    def update_selective(self, entity: SlackUser, slack_user_id):
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
        if entity.user_id is not None:
            update_info['user_id'] = entity.user_id
        if entity.user_name is not None:
            update_info['user_name'] = entity.user_name
        if entity.icon is not None:
            update_info['icon'] = entity.icon
        if entity.delete_flg is not None:
            update_info['delete_flg'] = entity.delete_flg

        self.execute_update(TABLE_ID, update_info, slack_user_id = slack_user_id)


    def delete(self, key: SlackUser):
        """
        Delete

        Args:
            key:

        Returns:

        """
        key_map = {}
        if key.slack_user_id is not None:
            key_map['slack_user_id'] = key.slack_user_id
        if key.user_id is not None:
            key_map['user_id'] = key.user_id
        if key.user_name is not None:
            key_map['user_name'] = key.user_name
        if key.icon is not None:
            key_map['icon'] = key.icon
        if key.delete_flg is not None:
            key_map['delete_flg'] = key.delete_flg

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

