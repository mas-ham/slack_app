"""
Slackからマスター情報を取得する

create 2025/05/09 hamada
"""
import os
import sys
import json

import requests
from tkinter import messagebox

from common import const
from common.logger.logger import Logger
from app_common import app_shared_service
from app_common.slack_service import SlackService
from dataaccess.entity.channel import Channel
from dataaccess.entity.slack_user import SlackUser
from dataaccess.general import channel_dataaccess, slack_user_dataaccess


class GetMasters:
    def __init__(self, logger:Logger, root_dir, bin_dir, conn, is_json=False):
        self.logger = logger
        self.root_dir = root_dir
        self.bin_dir = bin_dir
        self.conn = conn
        self.is_json = is_json

        # dataaccess
        self.channel_dataaccess = channel_dataaccess.ChannelDataAccess(conn)
        self.slack_user_dataaccess = slack_user_dataaccess.SlackUserDataAccess(conn)

        # SlackAPIトークンを取得
        token = app_shared_service.get_token()
        # Slackサービス
        if not is_json:
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
        user_list = self._get_user_list()
        self._regist_user_list(user_list)

        # チャンネル情報の取得
        # public、private、im、mpimと分けて取得する(レスポンスにtypeが返却されないため)
        public_channel_list = self._get_channel_list(const.PUBLIC_CHANNEL)
        private_channel_list = self._get_channel_list(const.PRIVATE_CHANNEL)
        im_channel_list = self._get_im_channel_list()

        self.channel_dataaccess.delete_all()
        self._regist_channel_list(public_channel_list)
        self._regist_channel_list(private_channel_list)
        self._regist_channel_list(im_channel_list)


    def _get_user_list(self):
        """
        Slackからユーザー情報を取得

        Returns:

        """

        # ユーザーリスト取得
        slack_user_list = []
        if self.is_json:
            with open(os.path.join(self.root_dir, 'import', 'get_messages', 'users.json'), 'r', encoding='utf-8') as f:
                result = json.load(f)
                for item in result:
                    slack_user_list.append(item)
        else:
            result = self.slack_service.get_user_list()
            slack_user_list = result['members']

        # slackから取得した情報を追加
        result_list = []
        for data in slack_user_list:
            # アイコンダウンロード
            response = None
            if not self.is_json:
                response = requests.get(data['profile']['image_24'])
                response.raise_for_status()
            if str(data['profile']['display_name']) == '':
                displayname = data['profile']['real_name']
                filename = data['id'] + '.jpg'
            else:
                displayname = data['profile']['display_name']
                filename = data['profile']['display_name'] + '.jpg'

            if not self.is_json:
                with open(os.path.join(app_shared_service.get_icon_dir(self.bin_dir), filename), 'wb') as f:
                    f.write(response.content)

            result_list.append({'user_id':data['id'], 'user_name':data['profile']['real_name'], 'user_display_name':displayname, 'icon':filename, 'delete_flg':data['deleted']})

        return result_list


    def _get_channel_list(self, channel_type):
        """
       Slackからチャンネル情報を取得(public/private)

        Args:
            channel_type:

        Returns:

        """

        # チャンネルリスト取得
        channel_list = []
        if self.is_json:
            if not channel_type == const.PUBLIC_CHANNEL:
                return []

            with open(os.path.join(self.root_dir, 'import', 'get_messages', 'channels.json'), 'r', encoding='utf-8') as f:
                result = json.load(f)
                for item in result:
                    channel_list.append(item)
        else:
            result = self.slack_service.get_channel_list(channel_type)
            channel_list = result['channels']

        # slackから取得した情報を追加
        result_list = []
        for data in channel_list:
            result_list.append({'channel_id': data['id'], 'channel_name': data['name'], 'channel_type': channel_type})

        return result_list


    def _get_im_channel_list(self):
        """
       Slackからチャンネル情報を取得(im)

        Args:

        Returns:

        """

        if self.is_json:
            return []

        # チャンネルリスト取得
        result = self.slack_service.get_channel_list('im')
        channel_list = result['channels']

        # slackから取得した情報を追加
        result_list = []
        for data in channel_list:
            # ユーザー名を取得
            user_id = self.slack_user_dataaccess.select_by_pk(data['user']).user_id
            result_list.append({'channel_id':data['id'], 'channel_name':user_id, 'channel_type':'im'})

        return result_list


    def _regist_user_list(self, user_list):
        """
        ユーザー情報を登録

        Args:
            user_list:

        Returns:

        """
        # 登録内容
        entity_list = []
        for row in user_list:
            entity = SlackUser(
                slack_user_id=row['user_id'],
                user_id = row['user_display_name'],
                user_name = row['user_name'],
                icon = row['icon'],
                delete_flg = app_shared_service.convert_flg(row['delete_flg']),
            )
            entity_list.append(entity)

        # Delete - Insert
        self.slack_user_dataaccess.delete_all()
        self.slack_user_dataaccess.insert_many(entity_list)


    def _regist_channel_list(self, channel_list):
        """
        チャンネル情報を登録

        Args:
            channel_list:

        Returns:

        """
        # 登録内容
        entity_list = []
        for row in channel_list:
            entity = Channel(
                channel_id=row['channel_id'],
                channel_name = row['channel_name'],
                channel_type = row['channel_type'],
            )
            entity_list.append(entity)

        # Insert
        self.channel_dataaccess.insert_many(entity_list)
