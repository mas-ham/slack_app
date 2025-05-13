import sys
import traceback
import pprint
import sqlite3

from tkinter import messagebox

from common import const, shared_service, sql_shared_service
from common.logger.logger import Logger
from .install import *


def execute(root_dir, bin_dir, logger: Logger):
    """
    メイン処理

    Args:
        root_dir:
        logger:

    Returns:

    """
    # 引数を取得
    params = shared_service.convert_py_parameters()
    print('Parameters')
    pprint.pprint(params)
    print('------------------------')

    shared_service.start_log(logger, params['application'], True)

    with sql_shared_service.get_connection(root_dir) as conn:
        match params['application']:
            case 'install':
                # チェック
                ans = messagebox.askyesno(None, '初回セットアップです\n実行してよろしいですか？')
                if ans:
                    install(bin_dir, conn)

            case _:
                pass

    shared_service.end_log(logger, params['application'], True)


if __name__ == '__main__':

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    logger: Logger = shared_service.set_logger()

    try:
        # メイン処理実行
        execute(root_dir, bin_dir, logger)

    except Exception as e:
        shared_service.print_except(e, logger)


