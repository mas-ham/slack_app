"""
Slackからマスター情報を取得する

create 2025/05/09 hamada
"""
import os
import sys

import requests
from tkinter import messagebox
import pandas as pd

from common import const
from common.logger.logger import Logger
from app_common import app_shared_service
from app_common.slack_service import SlackService


class GetMasters:
    def __init__(self, logger:Logger, root_dir, bin_dir):
        self.logger = logger
        self.root_dir = root_dir
        self.bin_dir = bin_dir

        # SlackAPIトークンを取得
        token = app_shared_service.get_token()
        # Slackサービス
        if token is None:
            self.logger.error('Not Define ENVIRONMENT_KEY [SLACK_API_TOKEN]')
            messagebox.showwarning('WARN', '環境変数「SLACK_API_TOKEN」が定義されていません')
            sys.exit()
        self.slack_service = SlackService(logger, token)


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
        df_user.to_excel(const.USER_FILENAME, sheet_name=const.USER_SHEET_NAME)
        # チャンネル情報の登録
        df_channel_public.to_excel(const.PUBLIC_CHANNEL_FILENAME, sheet_name=const.CHANNEL_SHEET_NAME)
        df_channel_private.to_excel(const.PRIVATE_CHANNEL_FILENAME, sheet_name=const.CHANNEL_SHEET_NAME)
        df_channel_im.to_excel(const.IM_CHANNEL_FILENAME, sheet_name=const.CHANNEL_SHEET_NAME)


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

            with open(os.path.join(app_shared_service.get_icon_dir(self.bin_dir), filename), 'wb') as f:
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

