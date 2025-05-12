"""
Slackから投稿を取得する

create 2025/05/09 hamada
"""
import os
import sys
import datetime
import time

from tkinter import messagebox
import pandas as pd
import openpyxl
from openpyxl.styles import Font
from openpyxl.styles.borders import Border, Side
from openpyxl.styles import Alignment, PatternFill
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import Rule
from openpyxl.drawing.image import Image

from common import const, shared_service
from common.logger.logger import Logger
from app_common import app_shared_service
from app_common.slack_service import SlackService

pd.options.display.float_format = '{:.6f}'.format


class GetMessages:
    def __init__(self, logger:Logger, root_dir, bin_dir):
        self.logger = logger
        self.root_dir = root_dir
        self.bin_dir = bin_dir

        # 設定ファイル
        self.conf = app_shared_service.get_conf(self.root_dir)['get_messages']
        # SlackAPIトークンを取得
        token = app_shared_service.get_token()
        # Slackサービス
        if int(self.conf['is_get_messages']):
            if token is None:
                self.logger.error('Not Define ENVIRONMENT_KEY [SLACK_API_TOKEN]')
                messagebox.showwarning('WARN', '環境変数「SLACK_API_TOKEN」が定義されていません')
                sys.exit()
            self.slack_service = SlackService(logger, token)


    def main(self):
        """
        Slackから投稿を取得

        Returns:

        """
        # public
        if int(self.conf['is_export_public']):
            channel_list_path, history_list_path, replies_list_path = app_shared_service.get_datafile(self.bin_dir, 'public')
            if int(self.conf['is_get_messages']):
                self._get_slack_messages(channel_list_path, history_list_path, replies_list_path)
            self._create_slack_messages(channel_list_path, history_list_path, replies_list_path, const.PUBLIC_DIR)

        # private
        if int(self.conf['is_export_private']):
            channel_list_path, history_list_path, replies_list_path = app_shared_service.get_datafile(self.bin_dir, 'private')
            if int(self.conf['is_get_messages']):
                self._get_slack_messages(channel_list_path, history_list_path, replies_list_path)
            self._create_slack_messages(channel_list_path, history_list_path, replies_list_path, const.PRIVATE_DIR)

        # im
        if int(self.conf['is_export_im']):
            channel_list_path, history_list_path, replies_list_path = app_shared_service.get_datafile(self.bin_dir, 'im')
            if int(self.conf['is_get_messages']):
                self._get_slack_messages(channel_list_path, history_list_path, replies_list_path)
            self._create_slack_messages(channel_list_path, history_list_path, replies_list_path, const.IM_DIR)

        # 設定ファイル更新
        # from_dateを前日に更新する
        if int(self.conf['is_get_messages']) and int(self.conf['is_overwrite_from_date']):
            json_data = app_shared_service.get_conf(self.root_dir)
            json_data['get_messages']['from_date'] = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y/%m/%d')
            app_shared_service.write_conf(self.root_dir, const.SETTINGS_FILENAME, json_data)


    def _get_slack_messages(self, channel_list_path, history_list_path, replies_list_path):
        """
        Slackからチャンネルタイプごとに投稿内容を取得

        Args:
            channel_list_path:
            history_list_path:
            replies_list_path:

        Returns:

        """

        # 対象チャネルを取得
        df_channel = pd.read_excel(channel_list_path, index_col=[0], names=('channel_id', 'channel_name', 'channel_type'))

        # 投稿情報、返信情報の取得
        df_history, df_replies = self._get_history_and_replies(df_channel, history_list_path, replies_list_path)

        # 投稿情報、返信情報の登録
        df_history.to_excel(history_list_path, sheet_name=const.HISTORY_SHEET_NAME)
        df_replies.to_excel(replies_list_path, sheet_name=const.REPLIES_SHEET_NAME)


    def _get_history_and_replies(self, df_channel, history_list_path, replies_list_path):
        """
        Slackから投稿内容と返信内容を取得

        Args:
            df_channel:
            history_list_path:
            replies_list_path:

        Returns:

        """

        # 既存の情報を取得
        df_history = pd.read_excel(history_list_path, index_col=[0], names=('index', 'channel_id', 'history_id', 'post_date', 'post_message', 'post_user'))
        df_replies = pd.read_excel(replies_list_path, index_col=[0], names=('index', 'channel_id', 'history_id', 'replies_id', 'reply_date', 'reply_message', 'reply_user'))

        df_history['history_id'] = df_history['history_id'].astype(float).astype(str)
        df_replies['history_id'] = df_replies['history_id'].astype(float).astype(str)
        df_replies['replies_id'] = df_replies['replies_id'].astype(float).astype(str)

        # Slackから投稿内容を取得
        history_dict = []
        replies_dict = []
        for channel_id in df_channel['channel_id']:
            self.get_channel_messages(channel_id, history_dict, replies_dict)

    #    if not history_dict and not replies_dict:
    #        return df_history, df_replies

        # 既存データと取得データとをマージ
        df_history_merge = pd.concat([df_history, pd.DataFrame(history_dict)])
        df_replies_merge = pd.concat([df_replies, pd.DataFrame(replies_dict)])
        # 重複削除
        df_history_merge.drop_duplicates(keep='last', subset=['channel_id', 'post_date', 'post_message'], inplace=True)
        df_replies_merge.drop_duplicates(keep='last', subset=['channel_id', 'reply_date', 'reply_message'], inplace=True)
        # 主キー項目がNaNのデータを除去して返却
        return df_history_merge, df_replies_merge
    #    return df_history_merge.dropna(axis=0, how='all', subset=['channel_id', 'history_id']), df_replies_merge.dropna(axis=0, how='all', subset=['channel_id', 'history_id', 'replies_id'])


    def get_channel_messages(self, channel_id, history_dict, replies_dict):
        """
        Slackのチャネル内の投稿内容と返信内容を取得

        Args:
            channel_id:
            history_dict:
            replies_dict:

        Returns:

        """

        # 投稿一覧を取得
        oldest, latest = self.get_term()
        time.sleep(1)
        result_history = self.slack_service.get_history(channel_id, limit=1000, oldest=oldest, latest=latest)

        if not result_history['ok']:
            self.logger.error('get history error:' + result_history['error'], is_print=True)
            return

        conversation_history = result_history['messages']

        while True:
            # 返信内容を取得
            for data_history in conversation_history:
                # slackから取得した情報を追加
                try:
                    post_date = datetime.datetime.fromtimestamp(int(str(data_history['ts']).split('.')[0]))
                    history_dict.append({'channel_id':channel_id, 'history_id':float(data_history['ts']), 'post_date':post_date, 'post_message':data_history['text'], 'post_user':data_history['user']})
                except Exception as e:
                    shared_service.print_except(e, self.logger)
                    self.logger.debug(','.join(f'{key}:{value}' for key, value in data_history.items()))
                    pass

                # 返信内容取得
                time.sleep(1.2)
                result_replies = self.slack_service.get_replies(channel_id, data_history['ts'])

                if not result_replies['ok']:
                    self.logger.error('get history error:' + result_replies['error'], is_print=True)
                    self.logger.debug(','.join(f'{key}:{value}' for key, value in data_history.items()))
                    break

                conversation_replies = result_replies['messages']

                for data_replies in conversation_replies:
                    if data_history['ts'] == data_replies['ts']:
                        # 返信内容には投稿自体の情報も含まれるため、投稿自体の情報は省く
                        continue

                    # slackから取得した情報を追加
                    try:
                        reply_date = datetime.datetime.fromtimestamp(int(str(data_replies['ts']).split('.')[0]))
                        replies_dict.append({'channel_id':channel_id, 'history_id':float(data_history['ts']), 'replies_id':float(data_replies['ts']), 'reply_date':reply_date, 'reply_message':data_replies['text'], 'reply_user':data_replies['user']})
                    except Exception as e:
                        shared_service.print_except(e, self.logger)
                        self.logger.debug(','.join(f'{key}:{value}' for key, value in data_replies.items()))
                        pass

            if not result_history['has_more']:
                break

            # 次の投稿一覧を取得
            result_history = self.slack_service.get_history_cursor(channel_id, result_history['response_metadata']['next_cursor'])

            if not result_history['ok']:
                self.logger.error('get history error:' + result_history['error'], is_print=True)
                break

            conversation_history = result_history['messages']


    def get_term(self):
        """
        投稿内容取得期間を取得

        Returns:

        """
        from_date = self.conf['from_date']
        to_date = self.conf['to_date']
        if not from_date:
            # Toが空の場合は1週間前を指定する
            from_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y/%m/%d')
        if not to_date:
            # Toが空の場合は前日を指定する
            to_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y/%m/%d')

        self.logger.info(f'get_messages : {from_date} - {to_date}', is_print=True)

        # UNIX時間に変換
        oldest = datetime.datetime.strptime(from_date, '%Y/%m/%d').timestamp()
        latest = datetime.datetime.strptime(to_date, '%Y/%m/%d').timestamp()

        return oldest, latest


    def _create_slack_messages(self, channel_list_path, history_list_path, replies_list_path, output_dir):
        """
        Slackから取得した投稿内容を成形する

        Args:
            channel_list_path:
            history_list_path:
            replies_list_path:
            output_dir:

        Returns:

        """
        # 各種情報取得
        df_channel = pd.read_excel(channel_list_path, index_col=[0], names=('index', 'channel_id', 'channel_name', 'channel_type'))
        df_user = pd.read_excel(os.path.join(self.bin_dir, const.DATA_DIR, const.USER_FILENAME), index_col=[0], names=('index', 'user_id', 'user_name', 'user_display_name', 'icon', 'delete_flg'))
        df_history = pd.read_excel(history_list_path, index_col=[0], names=('index', 'channel_id', 'history_id', 'post_date', 'post_message', 'post_user'))
        df_replies = pd.read_excel(replies_list_path, index_col=[0], names=('index', 'channel_id', 'history_id', 'replies_id', 'reply_date', 'reply_message', 'reply_user'))

        # マージ
        df_merge = pd.merge(df_history, df_replies, on=['channel_id', 'history_id'], how='left')
        df_merge = pd.merge(df_merge, df_channel, on='channel_id', how='left')
        df_merge = pd.merge(df_merge, df_user, left_on='post_user', right_on='user_id', how='left')
        df_merge = pd.merge(df_merge, df_user, left_on='reply_user', right_on='user_id', how='left')

        df_merge['no'] = 0
        df_output = (
            df_merge.drop(['history_id', 'replies_id', 'post_user', 'reply_user', 'channel_id', 'channel_type', 'user_id_x', 'user_id_y', 'delete_flg_x', 'delete_flg_y'], axis=1)
            .rename(
                columns={'user_display_name_x': 'post_name', 'user_display_name_y': 'reply_name', 'post_ts': 'post_date', 'reply_ts': 'reply_date', 'icon_x': 'post_icon', 'icon_y': 'reply_icon'})  # 列名変更
            .reindex(['channel_name', 'no', 'post_icon', 'post_name', 'post_date', 'post_message', 'reply_icon', 'reply_name', 'reply_date', 'reply_message'], axis=1)  # 列を定義
            .sort_values(by=['channel_name', 'post_date', 'reply_date'], ascending=[True, True, True])  # ソート
        )

        # チャネル単位に出力
        channel_name_list = list(dict.fromkeys(df_output.loc[:, 'channel_name']))
        for channel_name in channel_name_list:
            output_file = os.path.join(self.root_dir, const.EXPORT_DIR, output_dir, channel_name + '.xlsx')
            df_output.query('channel_name == "' + channel_name + '"').drop('channel_name', axis=1).reset_index(drop=True).to_excel(output_file, sheet_name=channel_name)

            # フォーマット
            wb = openpyxl.load_workbook(output_file)
            ws = wb.worksheets[0]

            ws.sheet_view.showGridLines = False
            ws.column_dimensions['B'].width = 10
            ws.column_dimensions['C'].width = 5
            ws.column_dimensions['D'].width = 15
            ws.column_dimensions['E'].width = 20
            ws.column_dimensions['F'].width = 60
            ws.column_dimensions['G'].width = 5
            ws.column_dimensions['H'].width = 15
            ws.column_dimensions['I'].width = 20
            ws.column_dimensions['J'].width = 60

            # 罫線
            side = Side(style='thin', color='000000')
            border_outline = Border(top=side, bottom=side, left=side, right=side)
            border_with_top = Border(top=side, bottom=None, left=side, right=side)
            border_side = Border(top=None, bottom=None, left=side, right=side)
            # border_none_bottom = Border(top=side, bottom=None, left=side, right=side)
            border_top = Border(top=side)

            # ヘッダ背景色
            fill_header = PatternFill(patternType='solid', fgColor='9FE2BF')

            # フォーマット
            font_base = Font(name='Meiryo UI', size=9)
            empty_font = Font(color='FFFFFF')

            # ヘッダのフォーマット
            for i in range(1, 11):
                ws.cell(row=1, column=i).border = border_outline
                ws.cell(row=1, column=i).fill = fill_header

            # 明細行のフォーマット
            row_index = 2
            no_val = 0
            bef_post_user = ''
            bef_post_date = ''
            while True:
                if ws.cell(row=row_index, column=1).value is None:
                    break

                # 書式設定
                ws.cell(row=row_index, column=1).alignment = Alignment(horizontal='center', vertical='top', wrap_text=False)
                ws.cell(row=row_index, column=2).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
                ws.cell(row=row_index, column=3).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
                ws.cell(row=row_index, column=4).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
                ws.cell(row=row_index, column=5).alignment = Alignment(horizontal='center', vertical='top', wrap_text=False)
                ws.cell(row=row_index, column=6).alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                ws.cell(row=row_index, column=7).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
                ws.cell(row=row_index, column=8).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
                ws.cell(row=row_index, column=9).alignment = Alignment(horizontal='center', vertical='top', wrap_text=False)
                ws.cell(row=row_index, column=10).alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                ws.cell(row=row_index, column=11).font = empty_font

                if bef_post_user == ws.cell(row=row_index, column=4).value \
                        and bef_post_date == ws.cell(row=row_index, column=5).value:
                    # 前行と投稿者、投稿日が同じ場合
                    # アイコンをクリア
                    ws.cell(row=row_index, column=3).value = None
                    # 同一グループフラグをONにする
                    ws.cell(row=row_index, column=11).value = '1'
                else:
                    # Noをインクリメント
                    no_val += 1
                    # 同一グループフラグをOFFにする
                    ws.cell(row=row_index, column=11).value = '0'

                    bef_post_user = ws.cell(row=row_index, column=4).value
                    bef_post_date = ws.cell(row=row_index, column=5).value

                # Noの設定
                ws.cell(row=row_index, column=2).value = no_val

                # 罫線の設定
                ws.cell(row=row_index, column=1).border = border_outline
                ws.cell(row=row_index, column=7).border = border_outline
                ws.cell(row=row_index, column=8).border = border_outline
                ws.cell(row=row_index, column=9).border = border_outline
                ws.cell(row=row_index, column=10).border = border_outline

                # 投稿者アイコン
                icon_name = str(ws.cell(row=row_index, column=3).value)
                img_path = os.path.join(app_shared_service.get_icon_dir(self.bin_dir), icon_name)
                if os.path.exists(img_path):
                    ws.cell(row=row_index, column=3).value = None
                    img = Image(img_path)
                    ws.add_image(img, ws.cell(row=row_index, column=3).coordinate)

                # 返信者アイコン
                icon_name = str(ws.cell(row=row_index, column=7).value)
                img_path = os.path.join(self.bin_dir, const.ICON_DIR, icon_name)
                if os.path.exists(img_path):
                    ws.cell(row=row_index, column=7).value = None
                    img = Image(img_path)
                    ws.add_image(img, ws.cell(row=row_index, column=7).coordinate)

                row_index += 1

            # 最下部の罫線
            ws.cell(row=row_index, column=2).border = border_top
            ws.cell(row=row_index, column=3).border = border_top
            ws.cell(row=row_index, column=4).border = border_top
            ws.cell(row=row_index, column=5).border = border_top
            ws.cell(row=row_index, column=6).border = border_top

            # フォーマット
            for row in ws:
                for cell in row:
                    ws[cell.coordinate].font = font_base
                    if 'K' in cell.coordinate:
                        cell.font = empty_font

            # 条件付き書式
            dxf = DifferentialStyle(border=border_side, font=empty_font)
            r = Rule(type='expression', dxf=dxf, stopIfTrue=True)
            r.formula = ['=INDIRECT(ADDRESS(ROW(), 11)) = "1"']
            ws.conditional_formatting.add('B2:F' + str(row_index - 1), r)

            dxf = DifferentialStyle(border=border_with_top)
            r = Rule(type='expression', dxf=dxf, stopIfTrue=True)
            r.formula = ['=INDIRECT(ADDRESS(ROW(), 11)) = "0"']
            ws.conditional_formatting.add('B2:F' + str(row_index - 1), r)

            # オートフィルタ
            ws.auto_filter.ref = ws.dimensions
            # ウィンドウ枠の固定
            ws.freeze_panes = 'B2'

            # 置換
            # 置換する文字列を指定
            bef_str_list = []
            aft_str_list = []

            # ユーザー
            for user_idx in range(len(df_user)):
                user = df_user.loc[user_idx]
                bef_str_list.append(user['user_id'])
                aft_str_list.append(user['user_display_name'])

            # 絵文字
            with open(os.path.join(self.root_dir, const.CONF_DIR, const.EMOJI_FILENAME)) as f:
                for data in f.readlines():
                    data = data.replace('\n', '')
                    bef_str_list.append(data.split()[0])
                    aft_str_list.append(chr(int(data.split()[1], 0)))

            i = 0
            # リストをループ
            for bef_str in bef_str_list:
                i += 1
                # セルをループ
                for row in ws.iter_rows():
                    for cell in row:
                        if cell.col_idx == 6 or cell.col_idx == 10:
                            # セルにリストが含まれていたら
                            if not cell.value is None and bef_str in cell.value:
                                # 置換
                                new_text = cell.value.replace(bef_str, aft_str_list[i - 1])
                                cell.value = new_text

            wb.save(output_file)

