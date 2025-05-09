"""
Slackからマスター情報を取得する

create 2025/05/09 hamada
"""
import os

import requests
import pandas as pd

from common import const
from common.logger.logger import Logger
from app_common import app_shared_service
from app_common.slack_service import SlackService


class GetMasters:
    def __init__(self, logger:Logger, root_dir, bin_dir, target_key):
        self.logger = logger
        self.root_dir = root_dir
        self.bin_dir = bin_dir
        self.target_key = target_key

        # 設定ファイル
        self.conf_slack_info = app_shared_service.get_conf(root_dir, const.CONF_SLACK_INFO, target_key)
        # Slackサービス
        self.slack_service = SlackService(logger, self.conf_slack_info['token'])


    def main(self):
        """
        Slackからマスター情報を取得

        Returns:

        """
        # ユーザー情報を取得
        df_user = self._get_user_list()
        # チャンネル情報の取得
        # public、private、im、mpimと分けて取得する(レスポンスにtypeが返却されないため)
        df_channel_public = self._get_channel_list('public_channel')
        df_channel_private = self._get_channel_list('private_channel')
        df_channel_im = self._get_channel_list('im',)

        # ユーザー情報の登録
        app_shared_service.regist_datafile(df_user, const.USER_FILENAME, const.USER_SHEET_NAME, [])
        # チャンネル情報の登録
        app_shared_service.regist_datafile(df_channel_public, const.PUBLIC_CHANNEL_FILENAME, const.CHANNEL_SHEET_NAME, [])
        app_shared_service.regist_datafile(df_channel_private, const.PRIVATE_CHANNEL_FILENAME, const.CHANNEL_SHEET_NAME, [])
        app_shared_service.regist_datafile(df_channel_im, const.IM_CHANNEL_FILENAME, const.CHANNEL_SHEET_NAME, [])


    def _get_user_list(self):
        """
        Slackからユーザー情報を取得

        Returns:

        """

        # ユーザーリスト取得
        result = self.slack_service.get_user_list()
        user_list = result['members']

        # slackから取得した情報を追加
        user_dict = []
        for data in user_list:
            # アイコンダウンロード
            response = requests.get(data['profile']['image_24'])
            response.raise_for_status()
            if str(data['profile']['display_name']) == '':
                displayname = data['profile']['real_name']
                filename = data['id'] + '.jpg'
            else:
                displayname = data['profile']['display_name']
                filename = data['profile']['display_name'] + '.jpg'

            with open(os.path.join(self.bin_dir, const.ICON_DIR, filename), 'wb') as f:
                f.write(response.content)

            user_dict.append({'user_id':data['id'], 'user_name':data['profile']['real_name'], 'user_display_name':displayname, 'icon':filename, 'delete_flg':data['deleted']})

        return pd.DataFrame(user_dict)


    def _get_channel_list(self, channel_type):
        """
       Slackからチャンネル情報を取得

        Args:
            channel_type:

        Returns:

        """

        # チャンネルリスト取得
        result = self.slack_service.get_channel_list(channel_type)
        channel_list = result['channels']

        # slackから取得した情報を追加
        channel_dict = []
        channel_name_key = 'user' if channel_type == 'im' else 'name'

        for data in channel_list:
            channel_dict.append({'channel_id': data['id'], 'channel_name': data[channel_name_key], 'channel_type': channel_type})

        return pd.DataFrame(channel_dict)


    def get_im_channel_list(self, channel_type):

        # チャンネルリスト取得
        result = self.slack_service.get_channel_list(channel_type)
        channel_list = result['channels']

        # slackから取得した情報を追加
        channel_dict = []
        for data in channel_list:
            channel_dict.append({'channel_id':data['id'], 'channel_name':data['user'], 'channel_type':channel_type})

        return pd.DataFrame(channel_dict)

