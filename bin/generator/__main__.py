import os
import traceback

from .generator import generate


if __name__ == '__main__':

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    table_list = [
        {'table_id': 'auth_user', 'autoincrement': False},
        {'table_id': 'channel', 'autoincrement': False},
        {'table_id': 'search_channel', 'autoincrement': False},
        {'table_id': 'search_user', 'autoincrement': False},
        {'table_id': 'slack_user', 'autoincrement': False},
        {'table_id': 'sso_user', 'autoincrement': False},
    ]
    try:
        generate(root_dir, bin_dir, table_list)

    except Exception as e:
        print(traceback.format_exception_only(type(e), e)[-1])

