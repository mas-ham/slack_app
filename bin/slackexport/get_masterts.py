"""
Slackからマスター情報を取得する

create 2025/05/09 hamada
"""
import os
import sys

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
    def __init__(self, logger:Logger, root_dir, bin_dir, conn):
        self.logger = logger
        self.root_dir = root_dir
        self.bin_dir = bin_dir
        self.conn = conn

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
        user_list = self._get_user_list()
        self._regist_user_list(user_list)

        # チャンネル情報の取得
        # public、private、im、mpimと分けて取得する(レスポンスにtypeが返却されないため)
        public_channel_list = self._get_channel_list(const.PUBLIC_CHANNEL)
        private_channel_list = self._get_channel_list(const.PRIVATE_CHANNEL)
        im_channel_list = self._get_im_channel_list()

        dataaccess = channel_dataaccess.ChannelDataAccess(self.conn)
        dataaccess.delete_all()
        self._regist_channel_list(public_channel_list)
        self._regist_channel_list(private_channel_list)
        self._regist_channel_list(im_channel_list)


    def _get_user_list(self):
        """
        Slackからユーザー情報を取得

        Returns:

        """

        # ユーザーリスト取得
        result = self.slack_service.get_user_list()
        slack_user_list = result['members']

        # slackから取得した情報を追加
        result_list = []
        for data in slack_user_list:
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

        # チャンネルリスト取得
        result = self.slack_service.get_channel_list('im')
        channel_list = result['channels']

        # slackから取得した情報を追加
        result_list = []
        for data in channel_list:
            # ユーザー名を取得
            dataaccess = slack_user_dataaccess.SlackUserDataAccess(self.conn)
            user_id = dataaccess.select_by_pk(data['user']).user_id
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
        dataaccess = slack_user_dataaccess.SlackUserDataAccess(self.conn)
        dataaccess.delete_all()
        dataaccess.insert_many(entity_list)


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

        # Delete - Insert
        dataaccess = channel_dataaccess.ChannelDataAccess(self.conn)
        dataaccess.insert_many(entity_list)
