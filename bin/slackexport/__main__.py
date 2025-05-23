"""
Slack投稿取得__main__

create 2023/04/05 TIS hamada
"""
import os
import sys
import pprint

from common import shared_service, sql_shared_service
from common.logger.logger import Logger


def execute(logger: Logger, root_dir, bin_dir):
    """
    メイン処理

    Args:
        logger:
        root_dir:
        bin_dir:

    Returns:

    """
    # 引数チェック
    if shared_service.is_invalid_param_num(logger, 1):
        # shared_service.result_error_return(root_dir, '引数が不正です')
        logger.error('引数が不正です', is_print=True)
        sys.exit()

    # 引数を取得
    params = shared_service.convert_py_parameters()
    print('Parameters')
    pprint.pprint(params)
    print('------------------------')

    shared_service.start_log(logger, params['application'], is_print=True)

    with sql_shared_service.get_connection(root_dir) as conn:
        match params['application']:
            case 'get_messages':
                # メッセージ取得
                # パフォーマンスを考慮し関数内でimport
                from slackexport.get_messages import GetMessages
                service = GetMessages(
                    logger,
                    root_dir,
                    bin_dir,
                    conn,
                    True if 'is_json' in params and int(params['is_json']) else False,
                )
                service.main()

                # 結果返却
                # shared_service.result_return(root_dir, {'status': status, 'message': message, 'data': result_list})

            case 'get_masters':
                # マスター情報取得
                # パフォーマンスを考慮し関数内でimport
                from slackexport.get_masterts import GetMasters
                service = GetMasters(
                    logger,
                    root_dir,
                    bin_dir,
                    conn,
                    True if 'is_json' in params and int(params['is_json']) else False,
                )
                service.main()

                # 結果返却
                # shared_service.result_return(root_dir, {'status': status, 'message': message, 'data': result_list})

            case _:
                pass

    shared_service.end_log(logger, params['application'], is_print=True)


if __name__ == '__main__':

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    logger: Logger = shared_service.set_logger()

    try:
        # メイン処理実行
        execute(logger, root_dir, bin_dir)

    except Exception as e:
        shared_service.print_except(e, logger)
        # shared_service.result_error_return(root_dir, traceback.format_exception_only(type(e), e)[-1])


