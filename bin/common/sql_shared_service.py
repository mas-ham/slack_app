"""
SQL共通サービス

create 2023/11/01 TIS hamada
"""
import os
import sqlite3


def get_connection(root_dir):
    """
    DB接続

    Returns:
        コネクション

    """

    # SQLite3
    return sqlite3.connect(os.path.join(root_dir, 'db', 'slack_app.db'))


def get_query(query_file_path):
    """
    SQLファイルからクエリーを取得

    Args:
        query_file_path:

    Returns:
        SQLクエリー

    """
    with open(query_file_path, 'r', encoding='utf-8') as f:
        query = f.read()
    return query


def is_empty(val):
    """
    Null(空文字含む)かどうか

    Args:
        val:

    Returns:
        bool値(true: Null or 空文字)

    """

    return val is None or val == ''


def null_to_empty(val):
    """
    Nullを空文字に変換

    Args:
        val:

    Returns:
        変換後の値

    """

    if val is None:
        return ''
    return val


