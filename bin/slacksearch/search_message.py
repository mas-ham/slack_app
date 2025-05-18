"""
Slackからエクスポートした情報から検索する

create 2025/05/10 hamada
"""
import os
import re

import pandas as pd
import bleach

from common import const
from app_common import app_shared_service
from dataaccess.ext import slack_search_dataaccess
from slacksearch.models import SlackSearchModel, SlackDetailModel, SlackResultModel


def get_poster_list(conn):
    """
    投稿者/返信者一覧を取得

    Args:
        conn:

    Returns:

    """
    dataaccess = slack_search_dataaccess.SlackSearchDataaccess(conn)
    results = dataaccess.get_poster_list()

    poster_list = []
    for _, row in results.iterrows():
        if row['user_id'] == 'deactivateduser':
            continue
        if row['display_flg'] is None or str(row['display_flg']) == '1':
            poster_list.append({
                'slack_user_id': row['slack_user_id'],
                'user_id': row['user_id'],
                'user_name': row['user_name'],
                'display_name': f"{row['user_id']}：{row['user_name']}",
                'checked': row['default_check_flg'],
            })

    return poster_list


def get_channel_list(conn):
    """
    チャンネル一覧を取得

    Args:
        conn:

    Returns:

    """
    dataaccess = slack_search_dataaccess.SlackSearchDataaccess(conn)
    results = dataaccess.get_channel_list()

    channel_list = []
    for _, row in results.iterrows():
        if row['display_flg'] is None or str(row['display_flg']) == '1':
            channel_list.append({
                'channel_id': row['channel_id'],
                'channel_type': row['channel_type'],
                'channel_name': row['channel_name'],
                'checked': row['default_check_flg'],
            })

    return channel_list


def search(conn, model: SlackSearchModel):
    """
    検索

    Args:
        conn:
        model:

    Returns:

    """

    channel_list = []
    channel_list.extend(model.public_channel_list)
    channel_list.extend(model.private_channel_list)
    channel_list.extend(model.im_channel_list)
    channel_list.extend(model.im_channel_list)
    dataaccess = slack_search_dataaccess.SlackSearchDataaccess(conn)
    # 検索
    result_list = dataaccess.search(
        model.poster_list,
        channel_list,
        model.search_val_list,
        model.search_type,
        model.is_contains_reply,
        app_shared_service.convert_from_date(model.search_from_date),
        app_shared_service.convert_to_date(model.search_to_date),
    )

    return _convert_to_json_for_search(result_list, model.search_val_list)


def _convert_to_json_for_search(record_list, search_val_list):
    """
    検索結果画面に返却する用にJSONへコンバート
    Args:
        record_list:

    Returns:

    """
    if record_list.empty:
        return []

    result_list = []
    before_key = ''
    for _, row in record_list.iterrows():
        if before_key == row['post_date']:
            continue

        result_list.append({
            'channel_name': row['channel_name'],
            'post_name': row['post_name'],
            'post_date': row['post_date'],
            'post_message': _add_highlights(row['post_message'], search_val_list),
            'channel_type': row['channel_type'],
        })

        before_key = row['post_date']

    return result_list


def get_detail(root_dir, model: SlackDetailModel) -> SlackResultModel:
    """
    詳細を取得

    Args:
        root_dir:
        model:

    Returns:

    """
    result = SlackResultModel()
    result.post_date = model.post_date
    df = pd.read_excel(os.path.join(root_dir, const.EXPORT_DIR, model.channel_type, f'{model.channel_name}.xlsx'), dtype=str).fillna('').query('post_date == "' + result.post_date + '"')

    result_list = []
    for _, row in df.iterrows():
        if not result.post_name:
            result.post_name = row['post_name']
            result.post_message = _add_highlights(row['post_message'], model.search_val_list)
        result_list.append({
            'reply_name': row['reply_name'],
            'reply_date': row['reply_date'],
            'reply_message': _add_highlights(row['reply_message'], model.search_val_list),
        })

    result.result_list = result_list
    return result


def _add_highlights(val, target_vals):
    """
    ハイライト表示

    Args:
        val:
        target_vals:

    Returns:

    """
    result = val
    for target_val in target_vals:
        pattern = re.compile(re.escape(target_val), re.IGNORECASE)
        result = pattern.sub(lambda match: f"<mark>{match.group()}</mark>", result)

    # サニタイズして返却
    allowed_tags = ['mark']
    return bleach.clean(result.replace('<!channel', '< !channel>'), tags=set(allowed_tags))

