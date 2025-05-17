"""
Slackエクスポート公開__main__

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

    match params['application']:
        case 'publish':
            # 公開用データを作成
            # パフォーマンスを考慮し関数内でimport
            from publish.publish import Publish
            service = Publish(
                logger,
                root_dir,
                bin_dir,
            )
            service.main()

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


