"""
Slackからマスター情報を取得する

create 2025/05/09 hamada
"""
import os
import sys
import sqlite3
import json

import requests
from tkinter import messagebox

from common import const
from common.logger.logger import Logger
from app_common import app_shared_service
from app_common.slack_service import SlackService
from dataaccess.entity.slack_user import SlackUser
from dataaccess.entity.search_channel import SearchChannel
from dataaccess.entity.search_user import SearchUser
from dataaccess.general import channel_dataaccess, slack_user_dataaccess, search_channel_dataaccess, search_user_dataaccess
from dataaccess.ext.slack_export_dataaccess import SlackExportDataaccess


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
        self.search_channel_dataaccess = search_channel_dataaccess.SearchChannelDataAccess(conn)
        self.search_user_dataaccess = search_user_dataaccess.SearchUserDataAccess(conn)
        self.slack_export_dataaccess = SlackExportDataaccess(conn.cursor())

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
        # トランザクションを開始
        self.conn.execute('BEGIN TRANSACTION')

        try:
            # ユーザー情報を登録
            user_list = self._get_user_list()
            self._regist_user_list(user_list)

            # チャンネル情報の取得
            if self.is_json:
                channel_list = self._get_channel_list_json()
            else:
                channel_list = self._get_channel_list()

            self._regist_channel_list(channel_list)

            # 検索用テーブルに登録
            self._regist_search_user_list(user_list)
            self._regist_search_channel_list(channel_list)

        except sqlite3.Error as e:
            self.conn.rollback()
            raise e


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


    def _get_channel_list(self):
        """
        Slackからチャンネル情報を取得

        Args:

        Returns:

        """

        # チャンネルリスト取得
        result = self.slack_service.get_channel_list(f'{const.PUBLIC_CHANNEL},{const.PRIVATE_CHANNEL},{const.IM_CHANNEL},{const.MPIM_CHANNEL}')
        channel_list = result['channels']

        # slackから取得した情報を追加
        result_list = []
        for data in channel_list:
            if 'is_im' in data and data['is_im']:
                channel_type = const.IM_CHANNEL
                channel_name = self._get_user_id(data['user'])
            elif 'is_mpim' in data and data['is_mpim']:
                channel_type = const.MPIM_CHANNEL
                channel_name = ','.join([self._get_user_id(u) for u in data['members']])
            elif 'is_group' in data and data['is_group']:
                channel_type = const.PRIVATE_CHANNEL
                channel_name = data['name']
            else:
                channel_type = const.PUBLIC_CHANNEL
                channel_name = data['name']
            result_list.append({'channel_id': data['id'], 'channel_name': channel_name, 'channel_type': channel_type})

        return result_list


    def _get_channel_list_json(self):
        """
        Slackからチャンネル情報を取得(Jsonより)

        Returns:

        """
        channel_list = []
        with open(os.path.join(self.root_dir, 'import', 'get_messages', 'channels.json'), 'r', encoding='utf-8') as f:
            result = json.load(f)
            for item in result:
                channel_list.append(item)

        result_list = []
        for data in channel_list:
            result_list.append({'channel_id': data['id'], 'channel_name': data['name'], 'channel_type': const.PUBLIC_CHANNEL})

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
        # 登録
        # 削除されたチャンネルはAPIでは取得できないため、UPSERTにする
        for row in channel_list:
            self.slack_export_dataaccess.upsert_channel({
                'channel_id': row['channel_id'],
                'channel_name': row['channel_name'],
                'channel_type': row['channel_type'],
            })


    def _regist_search_user_list(self, user_list):
        """
        検索用ユーザー情報を登録

        Args:
            user_list:

        Returns:

        """
        # 登録内容
        entity_list = []
        for row in user_list:
            org = self.search_user_dataaccess.select_by_pk(row['user_id'])
            if org is not None:
                continue
            entity = SearchUser(
                slack_user_id=row['user_id'],
                display_flg=1,
                default_check_flg=0,
            )
            entity_list.append(entity)

        if not entity_list:
            return
        # Insert
        self.search_user_dataaccess.insert_many(entity_list)


    def _regist_search_channel_list(self, channel_list):
        """
        検索用チャンネル情報を登録

        Args:
            channel_list:

        Returns:

        """
        # 登録内容
        entity_list = []
        for row in channel_list:
            org = self.search_channel_dataaccess.select_by_pk(row['channel_id'])
            if org is not None:
                continue
            entity = SearchChannel(
                channel_id=row['channel_id'],
                display_flg=1,
                default_check_flg=0,
            )
            entity_list.append(entity)

        if not entity_list:
            return
        # Insert
        self.search_channel_dataaccess.insert_many(entity_list)


    def _get_user_id(self, slack_user_id):
        """
        ユーザーID(Slackでの表示名)を取得

        Args:
            slack_user_id:

        Returns:

        """
        user = self.slack_user_dataaccess.select_by_pk(slack_user_id)
        if user is None:
            return ''
        return user.user_id
