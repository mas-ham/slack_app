"""
データアクセス層共通クラス

create 2024/03/29 TIS hamada
"""
import pandas as pd

from common import shared_service

# SQLログ出力フラグ
IS_EXPORT_SQL_LOG = True

# Select
SQL_SELECT = 'SELECT * FROM {} WHERE {}{}'

# Select by PK
SQL_SELECT_BY_PK = 'SELECT * FROM {} WHERE {}'

# Select all
SQL_SELECT_ALL = 'SELECT * FROM {}{}'

# Insert
SQL_INSERT = 'INSERT INTO {} ({}) VALUES ({})'

# Update
SQL_UPDATE = 'UPDATE {} SET {} WHERE {}'

# Delete
SQL_DELETE = 'DELETE FROM {} WHERE {}'

# Delete All
SQL_DELETE_ALL = 'DELETE FROM {}'

# Autoincrement値を取得
SQL_GET_LAST_ID = 'SELECT last_insert_rowid()'


class BaseDataAccess:
    """
    DataAccess基底クラス
    """
    def __init__(self, conn):
        self.conn = conn

    def execute_select(self, table_id, conditions: list, order_by_list: list | None) -> pd.DataFrame:
        """
        Select

        Args:
            table_id:
            conditions:
            order_by_list:

        Returns:

        """
        if not conditions:
            return self.execute_select_all(table_id, order_by_list)

        where_list = []
        params = []
        for condition in conditions:
            match condition.ope.lower():
                case 'eq':
                    where_list.append(f'{condition.key} = ?')
                    params.append(condition.val)
                case 'like':
                    where_list.append(f'{condition.key} LIKE ?')
                    params.append(f'%{condition.val}%')
                case 'orover':
                    where_list.append(f'{condition.key} >= ?')
                    params.append(condition.val)
                case 'over':
                    where_list.append(f'{condition.key} > ?')
                    params.append(condition.val)
                case 'orless':
                    where_list.append(f'{condition.key} <= ?')
                    params.append(condition.val)
                case 'less':
                    where_list.append(f'{condition.key} < ?')
                    params.append(condition.val)
                case 'in':
                    # FIXME: パラメーター上限999を超えたときにエラーが発生する
                    placeholder_list = ['?' for _ in condition.val]
                    val_list = [v for v in condition.val]
                    where_list.append(f'{condition.key} IN ({", ".join(placeholder_list)})')
                    params.extend(val_list)
                case _:
                    # FIXME:
                    where_list.append(f'{condition.key} = ?')
                    params.append(condition.val)

        query = SQL_SELECT.format(table_id, " AND ".join(where_list), _set_order_by(order_by_list))
        if IS_EXPORT_SQL_LOG:
            _write_sql_log(query, params)
        return pd.read_sql(query, self.conn, params=params)


    def execute_select_by_pk(self, table_id, **kwargs):
        """
        Select_by_PK

        Args:
            table_id:

        Returns:

        """
        where_list = []
        params = []
        for key, val in kwargs.items():
            where_list.append(f'{key} = ?')
            params.append(val)

        query = SQL_SELECT_BY_PK.format(table_id, " AND ".join(where_list))
        if IS_EXPORT_SQL_LOG:
            _write_sql_log(query, params)
        return pd.read_sql(query, self.conn, params=params)


    def execute_select_all(self, table_id, order_by_list: list):
        """
        Select_all

        Args:
            table_id:
            order_by_list:

        Returns:

        """
        query = SQL_SELECT_ALL.format(table_id, _set_order_by(order_by_list))
        if IS_EXPORT_SQL_LOG:
            _write_sql_log(query)
        return pd.read_sql(query, self.conn)


    def execute_insert(self, table_id, column_id_list, params):
        """
        Insert

        Args:
            table_id:
            column_id_list:
            params:

        Returns:

        """
        place_holder_list = ['?' for _ in range(len(column_id_list))]
        query = SQL_INSERT.format(table_id, ",".join(column_id_list), ",".join(place_holder_list))
        if IS_EXPORT_SQL_LOG:
            _write_sql_log(query, *params)

        cur = self.conn.cursor()
        cur.execute(query, params)
        cur.close()

        return self._get_last_id()


    def execute_insert_many(self, table_id, column_id_list, params):
        """
        Insert_many

        Args:
            table_id:
            column_id_list:
            params:

        Returns:

        """
        place_holder_list = ['?' for _ in range(len(column_id_list))]
        query = SQL_INSERT.format(table_id, ",".join(column_id_list), ",".join(place_holder_list))
        if IS_EXPORT_SQL_LOG:
            _write_sql_log(query, *params)

        cur = self.conn.cursor()
        # パラメーター数に上限があるため分割して実行
        batch_size = get_max_safe_batch_size(len(column_id_list))
        for i in range(0, len(params), batch_size):
            batch = params[i:i + batch_size]
            cur.executemany(query, batch)
        # cur.executemany(query, params)
        cur.close()


    def execute_update(self, table_id, update_info, **kwargs):
        """
        Update

        Args:
            table_id:
            update_info:

        Returns:

        """
        params = []
        update_key_list = []
        for key, val in update_info.items():
            update_key_list.append(f'{key} = ?')
            params.append(val)

        where_list = []
        for key, val in kwargs.items():
            where_list.append(f'{key} = ?')
            params.append(val)

        query = SQL_UPDATE.format(table_id, ",".join(update_key_list), " AND ".join(where_list))
        if IS_EXPORT_SQL_LOG:
            _write_sql_log(query, params)

        cur = self.conn.cursor()
        cur.execute(query, tuple(params))
        cur.close()



    def execute_delete(self, table_id, **kwargs):
        """
        Delete

        Args:
            table_id:

        Returns:

        """
        where_list = []
        for key, val in kwargs.items():
            where_list.append(f'{key} = ?')

        query = SQL_DELETE.format(table_id, " AND ".join(where_list))
        if IS_EXPORT_SQL_LOG:
            _write_sql_log(query, *kwargs.values())

        cur = self.conn.cursor()
        cur.execute(query, tuple(kwargs.values()))
        cur.close()


    def execute_delete_all(self, table_id):
        """
        Delete

        Args:
            table_id:

        Returns:

        """
        query = SQL_DELETE_ALL.format(table_id)
        if IS_EXPORT_SQL_LOG:
            _write_sql_log(query)

        cur = self.conn.cursor()
        cur.execute(query)
        cur.close()


    def _get_last_id(self):
        """
        SQLite3のAutoincrement値を取得

        Returns:

        """
        cur = self.conn.cursor()
        cur.execute(SQL_GET_LAST_ID)
        __last_id = cur.fetchone()[0]
        cur.close()
        return __last_id


def _set_order_by(order_by_list: list | None):
    """
    ORDER BY句生成

    Args:
        order_by_list:

    Returns:

    """
    if order_by_list is None:
        return ''
    list_ = []
    for order_by in order_by_list:
        asc_desc = ' DESC' if order_by.is_desc else ''
        list_.append(f'{order_by.key}{asc_desc}')

    return '' if not list_ else f" ORDER BY {', '.join(list_)}"


def get_max_safe_batch_size(num_columns, max_params=999):
    """
    executemanyのバッチサイズを取得

    Args:
        num_columns:
        max_params:

    Returns:

    """
    return max_params // num_columns


def _write_sql_log(sql, *args):
    """
    SQLログ出力

    Args:
        sql:
        *args:

    Returns:

    """
    try:
        logger = shared_service.set_sql_logger()
        logger.write_sql_log('', sql, *args)
    except Exception as e:
        print(e)
        pass

