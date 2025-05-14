"""
Slackから投稿を取得する

create 2025/05/09 hamada
"""
import os
import sqlite3
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
from dataaccess.common import set_cond_model, set_sort_model
from dataaccess.ext.slack_export_dataaccess import SlackExportDataaccess
from dataaccess.general.channel_dataaccess import ChannelDataAccess
from dataaccess.general.tr_channel_histories_dataaccess import TrChannelHistoriesDataAccess

pd.options.display.float_format = '{:.6f}'.format


class GetMessages:
    def __init__(self, logger:Logger, root_dir, bin_dir, conn):
        self.logger = logger
        self.root_dir = root_dir
        self.bin_dir = bin_dir
        self.conn = conn

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

        self.logger.info('get slack messages', is_print=True)

        # 期間を取得
        oldest, latest = self.get_term()

        cursor = self.conn.cursor()
        # トランザクションを開始
        self.conn.execute('BEGIN TRANSACTION')

        try:

            # public
            if int(self.conf['is_export_public']):
                channel_list_path, history_list_path, replies_list_path = app_shared_service.get_datafile(self.bin_dir, 'public')
                if int(self.conf['is_get_messages']):
                    self._get_slack_messages(cursor, const.PUBLIC_CHANNEL, oldest, latest)
                # FIXME: Excel作成は後でまとめてにする
                # self._create_slack_messages(channel_list_path, history_list_path, replies_list_path, const.PUBLIC_DIR)

            # private
            if int(self.conf['is_export_private']):
                channel_list_path, history_list_path, replies_list_path = app_shared_service.get_datafile(self.bin_dir, 'private')
                if int(self.conf['is_get_messages']):
                    self._get_slack_messages(cursor, const.PRIVATE_CHANNEL, oldest, latest)
                # FIXME: Excel作成は後でまとめてにする
                # self._create_slack_messages(channel_list_path, history_list_path, replies_list_path, const.PRIVATE_DIR)

            # im
            if int(self.conf['is_export_im']):
                channel_list_path, history_list_path, replies_list_path = app_shared_service.get_datafile(self.bin_dir, 'im')
                if int(self.conf['is_get_messages']):
                    self._get_slack_messages(cursor, const.IM_CHANNEL, oldest, latest)
                # FIXME: Excel作成は後でまとめてにする
                # self._create_slack_messages(channel_list_path, history_list_path, replies_list_path, const.IM_DIR)

            # コミット
            self.conn.commit()

            self.logger.info('export slack messages', is_print=True)
            self._create_slack_messages()

        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

        # 設定ファイル更新
        # from_dateを前日に更新する
        if int(self.conf['is_get_messages']) and int(self.conf['is_overwrite_from_date']):
            json_data = app_shared_service.get_conf(self.root_dir)
            json_data['get_messages']['from_date'] = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y/%m/%d')
            app_shared_service.write_conf(self.root_dir, const.SETTINGS_FILENAME, json_data)


    def _get_slack_messages(self, cursor, channel_type, oldest, latest):
        """
        Slackからチャンネルタイプごとに投稿内容を取得

        Args:
            cursor:
            channel_type:
            oldest:
            latest:

        Returns:

        """

        # 対象チャネルを取得
        # チャンネルの一覧を取得
        cond = [set_cond_model.Condition('channel_type', channel_type)]
        sort = [set_sort_model.OrderBy('channel_name')]
        dataaccess = ChannelDataAccess(self.conn)
        channel_list = dataaccess.select(cond, sort)

        history_list = []
        for channel in channel_list:
            # チャンネル単位で投稿内容、返信内容を取得
            history_list_ = self.get_channel_messages(channel.channel_id, oldest, latest)
            history_list.extend(history_list_)

        # 投稿内容、返信内容の登録
        dataaccess = SlackExportDataaccess(cursor)
        for history_info in history_list:
            history_params = (history_info['channel_id'], history_info['post_date'], history_info['post_user'], history_info['post_message'])
            dataaccess.upsert_history(history_params)
            # 登録されたID
            if cursor.lastrowid:
                channel_history_id = cursor.lastrowid
            else:
                # 既存のIDを取得
                channel_history_id = self.get_channel_history_id_by_logical_pk(history_info['post_date'])

            # 返信内容
            for reply_info in history_info['reply_list']:
                reply_params = (channel_history_id, reply_info['reply_date'], reply_info['reply_user'], reply_info['reply_message'])
                dataaccess.upsert_reply(reply_params)


    def get_channel_messages(self, channel_id, oldest, latest):
        """
        Slackのチャネル内の投稿内容と返信内容を取得

        Args:
            channel_id:
            oldest:
            latest:

        Returns:

        """
        history_list = []
        reply_list = []
        # 投稿一覧を取得
        time.sleep(1)
        result_history = self.slack_service.get_history(channel_id, limit=1000, oldest=oldest, latest=latest)

        if not result_history['ok']:
            self.logger.error('get history error:' + result_history['error'], is_print=True)
            return

        conversation_history = result_history['messages']

        while True:
            # 返信内容を取得
            for data_history in conversation_history:
                history_record = {}
                # slackから取得した情報を追加
                try:
                    post_date = datetime.datetime.fromtimestamp(int(str(data_history['ts']).split('.')[0]))
                    history_record = {'channel_id': channel_id, 'post_date':float(data_history['ts']), 'post_user': data_history['user'], 'post_message': data_history['text']}
                    # history_list.append({'channel_id': channel_id, 'post_date':float(data_history['ts']), 'post_user': data_history['user'], 'post_message': data_history['text']})
                except Exception as e:
                    shared_service.print_except(e, self.logger)
                    self.logger.debug(','.join(f'{key}:{value}' for key, value in data_history.items()))
                    pass

                # 返信内容取得
                # 1分間のリクエスト数に制限があるため待機
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
                        reply_list.append({'reply_date': float(data_replies['ts']), 'reply_user': data_replies['user'], 'reply_message': data_replies['text']})
                    except Exception as e:
                        shared_service.print_except(e, self.logger)
                        self.logger.debug(','.join(f'{key}:{value}' for key, value in data_replies.items()))
                        pass

                history_record['reply_list'] = reply_list
                history_list.append(history_record)

            if not result_history['has_more']:
                break

            # 次の投稿一覧を取得
            result_history = self.slack_service.get_history_cursor(channel_id, result_history['response_metadata']['next_cursor'])

            if not result_history['ok']:
                self.logger.error('get history error:' + result_history['error'], is_print=True)
                break

            conversation_history = result_history['messages']

        return history_list


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


    def _get_channel_list(self):
        sort = [
            set_sort_model.OrderBy('channel_type'),
            set_sort_model.OrderBy('channel_name')
        ]
        dataaccess = ChannelDataAccess(self.conn)
        return dataaccess.select_all(order_by_list=sort)


    def _create_slack_messages(self):
        """
        Slackから取得した投稿内容を成形する

        Args:

        Returns:

        """
        # チャンネル一覧を取得
        channel_list = self._get_channel_list()

        # チャンネルごとにExcelファイルを生成
        for channel in channel_list:
            self.logger.info(channel.channel_name, is_print=True)
            cursor = self.conn.cursor()
            dataaccess = SlackExportDataaccess(cursor)
            message_list = dataaccess.get_slack_messages((channel.channel_type, channel.channel_name))

            output_file = os.path.join(self.root_dir, const.EXPORT_DIR, channel.channel_type, f'{channel.channel_name}.xlsx')
            message_list.to_excel(output_file, sheet_name=channel.channel_name, index=False)

            self._format(output_file, channel.channel_name)
            # # フォーマット
            # wb = openpyxl.load_workbook(output_file)
            # ws = wb.worksheets[0]
            #
            # ws.sheet_view.showGridLines = False
            # ws.column_dimensions['A'].width = 10
            # ws.column_dimensions['B'].width = 5
            # ws.column_dimensions['C'].width = 15
            # ws.column_dimensions['D'].width = 20
            # ws.column_dimensions['E'].width = 60
            # ws.column_dimensions['F'].width = 5
            # ws.column_dimensions['G'].width = 15
            # ws.column_dimensions['H'].width = 20
            # ws.column_dimensions['I'].width = 60
            #
            # # 罫線
            # side = Side(style='thin', color='000000')
            # border_outline = Border(top=side, bottom=side, left=side, right=side)
            # border_with_top = Border(top=side, bottom=None, left=side, right=side)
            # border_side = Border(top=None, bottom=None, left=side, right=side)
            # # border_none_bottom = Border(top=side, bottom=None, left=side, right=side)
            # border_top = Border(top=side)
            #
            # # ヘッダ背景色
            # fill_header = PatternFill(patternType='solid', fgColor='9FE2BF')
            #
            # # フォーマット
            # font_base = Font(name='Meiryo UI', size=9)
            # empty_font = Font(color='FFFFFF')
            #
            # # ヘッダのフォーマット
            # for col in ws.iter_cols(min_col = 1, max_col = 9, min_row = 1, max_row = 1):
            #     col.border = border_outline
            #     col.fill = fill_header
            #
            # # 明細行のフォーマット
            # row_index = 2
            # no_val = 0
            # bef_post_user = ''
            # bef_post_date = ''
            #
            # for row in ws.iter_rows(min_row = 2, max_row = len(message_list) + 1, min_col = 1, max_col = 9):
            #     for cell in row:
            #         cell.border = border_outline
            #
            #     # 書式設定
            #     ws.cell(row=row_index, column=1).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            #     ws.cell(row=row_index, column=2).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            #     ws.cell(row=row_index, column=3).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            #     ws.cell(row=row_index, column=4).alignment = Alignment(horizontal='center', vertical='top', wrap_text=False)
            #     ws.cell(row=row_index, column=5).alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            #     ws.cell(row=row_index, column=6).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            #     ws.cell(row=row_index, column=7).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            #     ws.cell(row=row_index, column=8).alignment = Alignment(horizontal='center', vertical='top', wrap_text=False)
            #     ws.cell(row=row_index, column=9).alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            #
            #     if bef_post_user == ws.cell(row=row_index, column=3).value \
            #             and bef_post_date == ws.cell(row=row_index, column=4).value:
            #         # 前行と投稿者、投稿日が同じ場合
            #         # アイコン、メッセージをクリア
            #         ws.cell(row=row_index, column=1).value = None
            #         ws.cell(row=row_index, column=5).value = None
            #     else:
            #         # Noをインクリメント
            #         no_val += 1
            #
            #         bef_post_user = ws.cell(row=row_index, column=3).value
            #         bef_post_date = ws.cell(row=row_index, column=4).value
            #
            #     # Noの設定
            #     ws.cell(row=row_index, column=1).value = no_val
            #
            #     # 罫線の設定
            #     # ws.cell(row=row_index, column=1).border = border_outline
            #     ws.cell(row=row_index, column=6).border = border_outline
            #     ws.cell(row=row_index, column=7).border = border_outline
            #     ws.cell(row=row_index, column=8).border = border_outline
            #     ws.cell(row=row_index, column=9).border = border_outline
            #
            #     # 投稿者アイコン
            #     icon_name = str(ws.cell(row=row_index, column=2).value)
            #     img_path = os.path.join(app_shared_service.get_icon_dir(self.bin_dir), icon_name)
            #     if os.path.exists(img_path):
            #         ws.cell(row=row_index, column=2).value = None
            #         img = Image(img_path)
            #         ws.add_image(img, ws.cell(row=row_index, column=2).coordinate)
            #
            #     # 返信者アイコン
            #     icon_name = str(ws.cell(row=row_index, column=6).value)
            #     img_path = os.path.join(app_shared_service.get_icon_dir(self.bin_dir), icon_name)
            #     if os.path.exists(img_path):
            #         ws.cell(row=row_index, column=6).value = None
            #         img = Image(img_path)
            #         ws.add_image(img, ws.cell(row=row_index, column=6).coordinate)
            #
            #     row_index += 1
            #
            # # 最下部の罫線
            # ws.cell(row=row_index, column=1).border = border_top
            # ws.cell(row=row_index, column=2).border = border_top
            # ws.cell(row=row_index, column=3).border = border_top
            # ws.cell(row=row_index, column=4).border = border_top
            # ws.cell(row=row_index, column=5).border = border_top
            #
            # # フォーマット
            # for row in ws:
            #     for cell in row:
            #         ws[cell.coordinate].font = font_base
            #         # if 'K' in cell.coordinate:
            #         #     cell.font = empty_font
            #
            # # 条件付き書式
            # # dxf = DifferentialStyle(border=border_side, font=empty_font)
            # # r = Rule(type='expression', dxf=dxf, stopIfTrue=True)
            # # r.formula = ['=INDIRECT(ADDRESS(ROW(), 11)) = "1"']
            # # ws.conditional_formatting.add('B2:F' + str(row_index - 1), r)
            # #
            # # dxf = DifferentialStyle(border=border_with_top)
            # # r = Rule(type='expression', dxf=dxf, stopIfTrue=True)
            # # r.formula = ['=INDIRECT(ADDRESS(ROW(), 11)) = "0"']
            # # ws.conditional_formatting.add('B2:F' + str(row_index - 1), r)
            #
            # # オートフィルタ
            # ws.auto_filter.ref = ws.dimensions
            # # ウィンドウ枠の固定
            # ws.freeze_panes = 'B2'
            #
            # # 置換
            # # 置換する文字列を指定
            # bef_str_list = []
            # aft_str_list = []
            #
            # # # ユーザー
            # # for user_idx in range(len(df_user)):
            # #     user = df_user.loc[user_idx]
            # #     bef_str_list.append(user['user_id'])
            # #     aft_str_list.append(user['user_display_name'])
            # #
            # # # 絵文字
            # # with open(os.path.join(self.root_dir, const.CONF_DIR, const.EMOJI_FILENAME)) as f:
            # #     for data in f.readlines():
            # #         data = data.replace('\n', '')
            # #         bef_str_list.append(data.split()[0])
            # #         aft_str_list.append(chr(int(data.split()[1], 0)))
            # #
            # # i = 0
            # # # リストをループ
            # # for bef_str in bef_str_list:
            # #     i += 1
            # #     # セルをループ
            # #     for row in ws.iter_rows():
            # #         for cell in row:
            # #             if cell.col_idx == 6 or cell.col_idx == 10:
            # #                 # セルにリストが含まれていたら
            # #                 if not cell.value is None and bef_str in cell.value:
            # #                     # 置換
            # #                     new_text = cell.value.replace(bef_str, aft_str_list[i - 1])
            # #                     cell.value = new_text
            #
            # wb.save(output_file)

    def get_channel_history_id_by_logical_pk(self, post_date):
        cond = [set_cond_model.Condition('post_date', post_date)]
        dataaccess = TrChannelHistoriesDataAccess(self.conn)
        results = dataaccess.select(conditions=cond)

        return results[0].channel_id



    def _format(self, output_file, channel_name):

        column_settings = {
            1: ('left', 10),
            2: ('left', 5),
            3: ('left', 15),
            4: ('center', 20),
            5: ('left', 60),
            6: ('left', 5),
            7: ('left', 15),
            8: ('center', 20),
            9: ('left', 60),
        }

        # フォーマット
        wb = openpyxl.load_workbook(output_file)
        ws = wb.worksheets[0]

        for col_idx, (align, width) in column_settings.items():
            col_letter = openpyxl.utils.get_column_letter(col_idx)
            ws.column_dimensions[col_letter] = width

            for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=col_idx, max_col=col_idx):
                for cell in row:
                    cell.alignment = Alignment(horizontal=align)


        # ws.sheet_view.showGridLines = False
        # ws.column_dimensions['A'].width = 10
        # ws.column_dimensions['B'].width = 5
        # ws.column_dimensions['C'].width = 15
        # ws.column_dimensions['D'].width = 20
        # ws.column_dimensions['E'].width = 60
        # ws.column_dimensions['F'].width = 5
        # ws.column_dimensions['G'].width = 15
        # ws.column_dimensions['H'].width = 20
        # ws.column_dimensions['I'].width = 60

        # 罫線
        side = Side(style='thin', color='000000')
        border_outline = Border(top=side, bottom=side, left=side, right=side)
        border_top = Border(top=side)

        # ヘッダ背景色
        fill_header = PatternFill(patternType='solid', fgColor='9FE2BF')

        # フォーマット
        font_base = Font(name='Meiryo UI', size=9)

        # ヘッダのフォーマット
        for col in ws.iter_cols(min_col=1, max_col=9, min_row=1, max_row=1):
            col.border = border_outline
            col.fill = fill_header

        # 明細行のフォーマット
        row_index = 2
        no_val = 0
        bef_post_user = ''
        bef_post_date = ''

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=9):
            for cell in row:
                print(cell)
                cell.border = border_outline

            # # 書式設定
            # ws.cell(row=row_index, column=1).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            # ws.cell(row=row_index, column=2).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            # ws.cell(row=row_index, column=3).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            # ws.cell(row=row_index, column=4).alignment = Alignment(horizontal='center', vertical='top', wrap_text=False)
            # ws.cell(row=row_index, column=5).alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
            # ws.cell(row=row_index, column=6).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            # ws.cell(row=row_index, column=7).alignment = Alignment(horizontal='left', vertical='top', wrap_text=False)
            # ws.cell(row=row_index, column=8).alignment = Alignment(horizontal='center', vertical='top', wrap_text=False)
            # ws.cell(row=row_index, column=9).alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

            if bef_post_user == ws.cell(row=row_index, column=3).value \
                    and bef_post_date == ws.cell(row=row_index, column=4).value:
                # 前行と投稿者、投稿日が同じ場合
                # アイコン、メッセージをクリア
                ws.cell(row=row_index, column=1).value = None
                ws.cell(row=row_index, column=5).value = None
            else:
                # Noをインクリメント
                no_val += 1

                bef_post_user = ws.cell(row=row_index, column=3).value
                bef_post_date = ws.cell(row=row_index, column=4).value

            # Noの設定
            ws.cell(row=row_index, column=1).value = no_val

            # 罫線の設定
            # ws.cell(row=row_index, column=1).border = border_outline
            ws.cell(row=row_index, column=6).border = border_outline
            ws.cell(row=row_index, column=7).border = border_outline
            ws.cell(row=row_index, column=8).border = border_outline
            ws.cell(row=row_index, column=9).border = border_outline

            # 投稿者アイコン
            icon_name = str(ws.cell(row=row_index, column=2).value)
            img_path = os.path.join(app_shared_service.get_icon_dir(self.bin_dir), icon_name)
            if os.path.exists(img_path):
                ws.cell(row=row_index, column=2).value = None
                img = Image(img_path)
                ws.add_image(img, ws.cell(row=row_index, column=2).coordinate)

            # 返信者アイコン
            icon_name = str(ws.cell(row=row_index, column=6).value)
            img_path = os.path.join(app_shared_service.get_icon_dir(self.bin_dir), icon_name)
            if os.path.exists(img_path):
                ws.cell(row=row_index, column=6).value = None
                img = Image(img_path)
                ws.add_image(img, ws.cell(row=row_index, column=6).coordinate)

            row_index += 1

        # 最下部の罫線
        ws.cell(row=row_index, column=1).border = border_top
        ws.cell(row=row_index, column=2).border = border_top
        ws.cell(row=row_index, column=3).border = border_top
        ws.cell(row=row_index, column=4).border = border_top
        ws.cell(row=row_index, column=5).border = border_top

        # フォーマット
        for row in ws:
            for cell in row:
                ws[cell.coordinate].font = font_base
                # if 'K' in cell.coordinate:
                #     cell.font = empty_font

        # 条件付き書式
        # dxf = DifferentialStyle(border=border_side, font=empty_font)
        # r = Rule(type='expression', dxf=dxf, stopIfTrue=True)
        # r.formula = ['=INDIRECT(ADDRESS(ROW(), 11)) = "1"']
        # ws.conditional_formatting.add('B2:F' + str(row_index - 1), r)
        #
        # dxf = DifferentialStyle(border=border_with_top)
        # r = Rule(type='expression', dxf=dxf, stopIfTrue=True)
        # r.formula = ['=INDIRECT(ADDRESS(ROW(), 11)) = "0"']
        # ws.conditional_formatting.add('B2:F' + str(row_index - 1), r)

        # オートフィルタ
        ws.auto_filter.ref = ws.dimensions
        # ウィンドウ枠の固定
        ws.freeze_panes = 'B2'

        # 置換
        # 置換する文字列を指定
        bef_str_list = []
        aft_str_list = []

        # # ユーザー
        # for user_idx in range(len(df_user)):
        #     user = df_user.loc[user_idx]
        #     bef_str_list.append(user['user_id'])
        #     aft_str_list.append(user['user_display_name'])
        #
        # # 絵文字
        # with open(os.path.join(self.root_dir, const.CONF_DIR, const.EMOJI_FILENAME)) as f:
        #     for data in f.readlines():
        #         data = data.replace('\n', '')
        #         bef_str_list.append(data.split()[0])
        #         aft_str_list.append(chr(int(data.split()[1], 0)))
        #
        # i = 0
        # # リストをループ
        # for bef_str in bef_str_list:
        #     i += 1
        #     # セルをループ
        #     for row in ws.iter_rows():
        #         for cell in row:
        #             if cell.col_idx == 6 or cell.col_idx == 10:
        #                 # セルにリストが含まれていたら
        #                 if not cell.value is None and bef_str in cell.value:
        #                     # 置換
        #                     new_text = cell.value.replace(bef_str, aft_str_list[i - 1])
        #                     cell.value = new_text

        wb.save(output_file)
