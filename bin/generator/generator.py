"""
dataacceess generator

create 2024/03/29 hamada
"""
import os
import datetime

from common import sql_shared_service

AUTHOR = 'hamada'

def generate(root_dir, bin_dir, table_list):

    with sql_shared_service.get_connection(root_dir) as conn:
        cur = conn.cursor()

        for table_info in table_list:
            table_id = table_info['table_id']
            print(table_id)
            cur.execute(f'PRAGMA table_info({table_id})')

            is_autoincrement = table_info['autoincrement']
            column_list = list()
            pk_list = list()
            all_list = list()
            records = cur.fetchall()

            if len(records) == 0:
                continue

            for row in records:
                # PK
                if row[5] > 0:
                    pk_list.append(row[1])

                # column
                if is_autoincrement:
                    # autoincrementの場合は主キー以外のみ格納
                    if row[5] == 0:
                        column_list.append(row[1])
                else:
                    column_list.append(row[1])

                # all_list
                all_list.append(row[1])

            _create_entity(bin_dir, table_id, column_list, pk_list, all_list)
            _create_dataaccess(bin_dir, table_id, column_list, pk_list, all_list)


def _create_entity(root_dir, table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    joined_col_list = ', '.join([f'{s} = None' for s in all_list])
    s = list()
    s.append(f'"""')
    s.append(f'Entity：{table_id}')
    s.append(f'')
    s.append(f'create {date} {AUTHOR}')
    s.append(f'"""')
    s.append(f'import dataclasses')
    s.append(f'')
    s.append(f'')
    s.append(f'@dataclasses.dataclass')
    s.append(f'class {camel_table_id}:')
    for column_id in all_list:
        s.append(f'    {column_id} = None')
    s.append(f'')
    s.append(f'    def __init__(self, {joined_col_list}):')
    for column_id in all_list:
        s.append(f'        self.{column_id} = {column_id}')
    s.append(f'')

    export_dir = os.path.join(root_dir, 'dataaccess', 'entity')
    os.makedirs(export_dir, exist_ok=True)
    with open(os.path.join(export_dir, f'{table_id}.py'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(s))


def _create_dataaccess(root_dir, table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    s.extend(_create_dataaccess_header(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_select(table_id, column_list, pk_list, all_list))
    # s.extend(_create_dataaccess_select2(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_select_by_pk(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_select_all(table_id, column_list, pk_list, all_list))
    # s.extend(_create_dataaccess_select_all2(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_insert(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_insert_many(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_update(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_update_selective(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_delete(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_delete_by_pk(table_id, column_list, pk_list, all_list))
    s.extend(_create_dataaccess_delete_all(table_id, column_list, pk_list, all_list))

    export_dir = os.path.join(root_dir, 'dataaccess', 'general')
    os.makedirs(export_dir, exist_ok=True)
    with open(os.path.join(export_dir, f'{table_id}_dataaccess.py'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(s))


def _create_dataaccess_header(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    s.append(f'"""')
    s.append(f'dataaccess：{table_id}')
    s.append(f'')
    s.append(f'create {date} {AUTHOR}')
    s.append(f'"""')
    s.append(f'from dataaccess.common.base_dataaccess import BaseDataAccess')
    s.append(f'from dataaccess.entity.{table_id} import {camel_table_id}')
    s.append(f'')
    s.append(f'')
    s.append(f"TABLE_ID = '{table_id}'")
    s.append(f'')
    s.append(f'class {camel_table_id}DataAccess(BaseDataAccess):')
    s.append(f'    def __init__(self, conn):')
    s.append(f'        super().__init__(conn)')
    s.append(f'')
    s.append(f'        self.col_list = [')
    for column_id in column_list:
        s.append(f"            '{column_id}',")
    s.append(f'        ]')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_select(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    row_list = []
    for column_id in column_list:
        row_list.append(f"row['{column_id}']")
    s = list()
    # Select
    s.append(f'    def select(self, conditions: list, order_by_list = None) -> list[{camel_table_id}]:')
    s.append(f'        """')
    s.append(f'        Select')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            conditions:')
    s.append(f'            order_by_list:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'')
    s.append(f'        results = self.execute_select(TABLE_ID, conditions, order_by_list)')
    s.append(f'        if results.empty:')
    s.append(f'            return []')
    s.append(f'        return [{camel_table_id}({", ".join(row_list)}) for _, row in results.iterrows()]')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_select2(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    pl_list = [f'l[{i}][i]' for i in range(len(all_list))]
    s = list()
    # Select
    s.append(f'    def select2(self, conditions: list, order_by_list = None) -> pl.DataFrame:')
    s.append(f'        """')
    s.append(f'        Select')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            conditions:')
    s.append(f'            order_by_list:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'')
    s.append(f'        return self.execute_select(TABLE_ID, conditions, order_by_list)')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_select_by_pk(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    row_list = []
    for column_id in column_list:
        row_list.append(f"results[0]['{column_id}']")
    s = list()
    # Select_by_PK
    s.append(f'    def select_by_pk(self, {", ".join(pk_list)}) -> {camel_table_id} | None:')
    s.append(f'        """')
    s.append(f'        Select_by_PK')
    s.append(f'')
    s.append(f'        Args:')
    for column_id in pk_list:
        s.append(f'            {column_id}:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        results = self.execute_select_by_pk(TABLE_ID, {pk_param})')
    s.append(f'        if results.empty:')
    s.append(f'            return None')
    s.append(f'        return {camel_table_id}({", ".join(row_list)})')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_select_all(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    row_list = []
    for column_id in column_list:
        row_list.append(f"row['{column_id}']")
    s = list()
    # Select_by_PK
    s.append(f'    def select_all(self, order_by_list = None) -> list[{camel_table_id}]:')
    s.append(f'        """')
    s.append(f'        Select_all')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            order_by_list:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        results = self.execute_select_all(TABLE_ID, order_by_list)')
    s.append(f'        if results.empty:')
    s.append(f'            return []')
    s.append(f'        return [{camel_table_id}({", ".join(row_list)}) for _, row in results.iterrows()]')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_select_all2(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    pl_list = [f'l[{i}][i]' for i in range(len(all_list))]
    s = list()
    # Select_by_PK
    s.append(f'    def select_all2(self, order_by_list = None) -> pl.DataFrame:')
    s.append(f'        """')
    s.append(f'        Select_all')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            order_by_list:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        return self.execute_select_all(TABLE_ID, order_by_list)')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_insert( table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    # Insert
    s.append(f'    def insert(self, entity: {camel_table_id}) -> int:')
    s.append(f'        """')
    s.append(f'        Insert')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            entity:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        params = (')
    for column_id in column_list:
        s.append(f"            entity.{column_id},")
    s.append(f'        )')
    s.append(f'        return self.execute_insert(TABLE_ID, self.col_list, params)')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_insert_many(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    # Insert_many
    s.append(f'    def insert_many(self, entity_list: list):')
    s.append(f'        """')
    s.append(f'        Insert_many')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            entity_list:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        params = []')
    s.append(f'        for entity in entity_list:')
    s.append(f'            params.append(')
    s.append(f'                (')
    for column_id in column_list:
        s.append(f"                    entity.{column_id},")
    s.append(f'                )')
    s.append(f'            )')
    s.append(f'        self.execute_insert_many(TABLE_ID, self.col_list, params)')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_update(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    # Update
    s.append(f'    def update(self, entity: {camel_table_id}, {", ".join(pk_list)}):')
    s.append(f'        """')
    s.append(f'        Update')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            entity:')
    for column_id in pk_list:
        s.append(f'            {column_id}:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        update_info = {{')
    for column_id in column_list:
        s.append(f"            '{column_id}': entity.{column_id},")
    s.append(f'        }}')
    s.append(f'        self.execute_update(TABLE_ID, update_info, {pk_param})')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_update_selective(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    # Update_selective
    s.append(f'    def update_selective(self, entity: {camel_table_id}, {", ".join(pk_list)}):')
    s.append(f'        """')
    s.append(f'        Update selective')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            entity:')
    for column_id in pk_list:
        s.append(f'            {column_id}:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        update_info = {{}}')
    for column_id in column_list:
        s.append(f"        if entity.{column_id} is not None:")
        s.append(f"            update_info['{column_id}'] = entity.{column_id}")
    s.append(f'')
    s.append(f'        self.execute_update(TABLE_ID, update_info, {pk_param})')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_delete_by_pk(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    # Delete_by_PK
    s.append(f'    def delete_by_pk(self, {", ".join(pk_list)}):')
    s.append(f'        """')
    s.append(f'        Delete_by_PK')
    s.append(f'')
    s.append(f'        Args:')
    for column_id in pk_list:
        s.append(f'            {column_id}:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        self.execute_delete(TABLE_ID, {pk_param})')
    s.append(f'')
    s.append(f'')

    return s

def _create_dataaccess_delete_all(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    # Delete_by_PK
    s.append(f'    def delete_all(self):')
    s.append(f'        """')
    s.append(f'        Delete_All')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        self.execute_delete(TABLE_ID)')
    s.append(f'')
    s.append(f'')

    return s


def _create_dataaccess_delete(table_id, column_list, pk_list, all_list):
    camel_table_id = _convert_camel(table_id)
    date = datetime.datetime.now().strftime('%Y/%m/%d')
    pk_params = []
    for column_id in pk_list:
        pk_params.append(f'{column_id} = {column_id}')
    pk_param = ', '.join(pk_params)
    s = list()
    # Delete
    s.append(f'    def delete(self, key: {camel_table_id}):')
    s.append(f'        """')
    s.append(f'        Delete')
    s.append(f'')
    s.append(f'        Args:')
    s.append(f'            key:')
    s.append(f'')
    s.append(f'        Returns:')
    s.append(f'')
    s.append(f'        """')
    s.append(f'        key_map = {{}}')
    for column_id in all_list:
        s.append(f"        if key.{column_id} is not None:")
        s.append(f"            key_map['{column_id}'] = key.{column_id}")
    s.append(f'')
    s.append(f'        self.execute_delete(TABLE_ID, **key_map)')
    s.append(f'')
    s.append(f'')

    return s




def _convert_camel(val):
    return ''.join(word.capitalize() for word in val.split('_'))
