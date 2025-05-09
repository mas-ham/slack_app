"""
共通サービス

create 2023/11/01 TIS hamada
"""
import os
import sys
import json
import traceback
import warnings

from PIL import ImageColor

# from common import const
from common.logger import logger, sql_logger


def convert_to_upper(val: str) -> str:
    """
    大文字変換

    Args:
        val: 対象の値

    Returns:
        変換後の値

    """
    if val is None or val == '':
        return ''
    return val.upper()


def convert_to_lower(val: str) -> str:
    """
    小文字変換

    Args:
        val: 対象の値

    Returns:
        変換後の値

    """
    if val is None or val == '':
        return ''
    return val.lower()


def get_basename(filename) -> str:
    """
    拡張子を除いたファイル名を取得

    Args:
        filename:

    Returns:

    """
    return os.path.splitext(os.path.basename(filename))[0]


def empty_to_none(val):
    """
    空文字をNoneに変換

    Args:
        val:

    Returns:

    """
    return None if val == '' else val


def result_return(root_dir, result):
    """
    結果jsonをファイルに出力

    Args:
        root_dir:
        result:

    """
    # ディレクトリ作成
    json_dir = os.path.join(root_dir, 'result')
    if not os.path.isdir(json_dir):
        os.makedirs(json_dir, exist_ok=True)

    # 既存ファイルを削除
    json_file = os.path.join(json_dir, 'result.json')
    if os.path.isfile(json_file):
        os.remove(json_file)

    # jsonをファイルに出力
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False))


def result_plane_return(root_dir, result, result_filename):
    """
    結果をファイルに出力

    Args:
        root_dir:
        result:
        result_filename:

    """
    # ディレクトリ作成
    result_dir = os.path.join(root_dir, 'result')
    if not os.path.isdir(result_dir):
        os.makedirs(result_dir, exist_ok=True)

    # 既存ファイルを削除
    json_file = os.path.join(result_dir, result_filename)
    if os.path.isfile(json_file):
        os.remove(json_file)

    # jsonをファイルに出力
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(result)


# def result_error_return(root_dir, error_message='', status=const.EXCEPTION):
#     """
#     エラー時の返却処理
#
#     Args:
#         root_dir:
#         error_message:
#         status:
#
#     Returns:
#
#     """
#     # print(error_message)
#     result_return(root_dir, {'status': status, 'message': f'エラーが発生しました。\n{error_message}', 'data': []})


def split_code_name(val: str):
    """
    コードと名称を分割する

    Args:
        val:

    Returns:
        コード値
        名称

    """
    if val == '':
        return '', ''

    if ':' in val:
        return val.split(':')[0], val.split(':')[1]

    return val, ''


def convert_rgb(hex_number):
    """
    16進数をRGBに変換

    Args:
        hex_number:

    Returns:

    """
    if hex_number.startswith('#'):
        hex_code = hex_number
    else:
        hex_code = f'#{hex_number}'
    rgb_color = ImageColor.getcolor(hex_code, 'RGB')

    return rgb_color[0], rgb_color[1], rgb_color[2]


# def convert_to_excel_data(row_list):
#     """
#     Excelへの返却用に形式を変換する
#     dictのリストをパラメーターとして指定する
#     dictのキー:column_listに格納されているデータをcolumnXとして格納しなおす
#     各行データの列数を算出してdictに追加する
#
#     Args:
#         row_list:
#
#     Returns:
#         dict {'record_count', 'excel_data', 'column_count'}
#
#     """
#     result_list = []
#     max_column_count = 0
#     for row_data in row_list:
#         result = {}
#
#         # 列情報を取出し
#         column_list = row_data[const.KEY_COLUMN_LIST]
#         i = 1
#         for col_data in column_list:
#             result[f'column{i}'] = empty_to_none(col_data)
#             i += 1
#
#         # 元々のキー情報を移管
#         for key in row_data:
#             if key == const.KEY_COLUMN_LIST:
#                 continue
#             result[key] = row_data.get(key)
#
#         # エントリー数
#         column_count = len(column_list)
#         result['count'] = column_count
#
#         # 1行あたりの列数の最大値を算出
#         if column_count > max_column_count:
#             max_column_count = column_count
#
#         # リストに格納
#         result_list.append(result)
#
#     return {
#         'record_count': len(result_list),
#         'excel_data': result_list,
#         'column_count': max_column_count,
#     }


def ignore_user_warning():
    """
    入力規則のあるExcelを読み込む時のWarningを無視する

    Returns:

    """
    warnings.simplefilter(action='ignore', category=UserWarning)


def convert_py_parameters() -> dict:
    """
    python実行時のパラメーターをdictに変換

    Returns:
        変換後パラメーター

    """
    result = {}
    for i in range(1, len(sys.argv)):
        splited = sys.argv[i].split('=')
        result[splited[0]] = splited[1] if len(splited) > 1 else ''
    return result


def is_invalid_param_num(logger:logger.Logger, param_num) -> bool:
    """
    パラメーター数チェック

    Args:
        logger: ロガー
        param_num: 外部から渡す引数の数

    Returns:

    """
    # 自動で第1引数としてパスが追加されるのを考慮
    if (len(sys.argv)) < param_num + 1:
        logger.error(f'引数不正(Expect:{param_num},Actual:{len(sys.argv)-1})')
        return True
    return False


def check_selected(tree_view, is_single) -> str:
    """
    TreeViewの選択状態チェック

    Args:
        tree_view:
        is_single:

    Returns:

    """
    selected_items = tree_view.selection()
    if not selected_items:
        return '選択されていません'
    if is_single and len(selected_items) > 1:
        return '複数選択されています'

    return ''


def set_logger():
    """
    Loggerのセットアップ

    Args:

    Returns:
        ロガークラス

    """
    # Loggerの設定
    return logger.Logger(
        get_log_dir(),
    )


def set_sql_logger():
    """
    SqlLoggerのセットアップ

    Args:

    Returns:
        ロガークラス

    """
    # SqlLoggerの設定
    return sql_logger.SqlLogger(
        get_log_dir(),
    )


def get_log_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  'log'))


def start_log(logger: logger.Logger, program_id='', is_print=False):
    """
    処理開始ログの出力

    Args:
        logger:
        program_id:
        is_print:

    """
    try:
        if logger is None:
            return

        logger.info(f'Start {program_id}', is_print=is_print)
    except Exception:
        # Exception発生時は無視する
        pass


def end_log(logger: logger.Logger, program_id='', is_print=False):
    """
    処理終了ログの出力

    Args:
        logger:
        program_id:
        is_print:

    """
    try:
        if logger is None:
            return

        logger.info(f'End    {program_id}', is_print=is_print)
    except Exception:
        # Exception発生時は無視する
        pass


def print_except(e, logger: logger.Logger=None):
    """
    Exceptionログを出力

    Args:
        e:
        logger:

    """
    if logger is not None:
        logger.error(traceback.format_exception_only(type(e), e)[-1])
        logger.write_exception_log(traceback.format_exc())


