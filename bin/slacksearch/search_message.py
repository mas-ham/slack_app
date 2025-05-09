import os

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
import textwrap
import pandas as pd

from common import const
from common.logger.logger import Logger
from common.base_view import BaseView

# 結果画面
VIEW_RESULT_W = 1350
VIEW_RESULT_H = 900
FRAME_RESULT_W = VIEW_RESULT_W - 60



class SearchMessage(BaseView):
  def __init__(self, logger: Logger, root_dir, bin_dir, callback=None, master=None) -> None:
    super().__init__(bg='white', height=800, width=1000, master=master)


# **********************************
# 検索画面
# **********************************

#
# 閉じる
#
def do_close():
  view.destroy()

#
# 全選択(投稿者/返信者)
#
def all_check_member_list():
  flg = val_all_chk_poster.get()
  for i in range(len(val_poster)):
    val_poster[i].set(flg)

#
# 全選択(channel)
#
def all_check_channel_list():
  flg = val_all_chk_channel.get()
  for i in range(len(val_channel)):
    val_channel[i].set(flg)

#
# 検索
#
def do_search():

  # **********************************
  # 検索結果画面
  # **********************************

  #
  # 閉じる
  #
  def close_result_view():
    view_result.destroy()

  # ★バグ対応用の関数を追加
  def fixed_map(option):
    return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]

  #
  # 検索処理
  #
  def search(channel_name):
    filename = os.path.join(const.public_output_dir, channel_name + '.xlsx')
    df_all = pd.read_excel(filename, index_col=[0], names=('no', 'post_icon', 'post_name', 'post_date', 'post_message', 'reply_icon', 'reply_name', 'reply_date', 'reply_message', 'group_flg'))
    df_all['post_message'] = df_all['post_message'].astype(str)
    df_all['reply_name'] = df_all['reply_name'].astype(str)
    df_all['reply_date'] = df_all['reply_date'].astype(str)
    df_all['reply_message'] = df_all['reply_message'].astype(str)
    df_all['group_flg'] = df_all['group_flg'].astype(str)
    df_all['channel_name'] = channel_name

    if len(srch_list) == 0:
      # 検索条件未指定の場合、ユーザーのみ絞り込み
      if len(srch_user_list) == 0:
        return df_all
      # 先に返信者で絞り込み
      df_work2 = df_all[df_all['reply_name'].isin(srch_user_list)]
      return df_work2[df_work2['post_name'].isin(srch_user_list)]

    df_work_list = []
    for srch_str in srch_list:
      # 投稿
      df_work1 = df_all.query('group_flg == "0"')
      if len(srch_user_list) > 0:
        df_work1 = df_work1[df_work1['post_name'].isin(srch_user_list)]
      df_work1 = df_work1[df_work1['post_message'].str.contains(srch_str)]
      # 返信
      df_work2 = df_all
      if len(srch_user_list) > 0:
        df_work2 = df_work2[df_work2['reply_name'].isin(srch_user_list)]
      df_work2 = df_work2[df_work2['reply_message'].str.contains(srch_str)]

      # マージ
      df_work = pd.concat([df_work1, df_work2])
      df_work_list.append(df_work.groupby(df_work.index).first())

    df_base = df_work_list[0]
    for i in range(1, len(df_work_list)):
      if val_srch_type.get() == 0:
        # AND検索の場合
        df_base = pd.merge(df_base, df_work_list[i], how='inner')
      else:
        # OR検索の場合
        df_base = pd.concat([df_base, df_work_list[i]])
        df_base = df_base.groupby(df_base.index).first()

    return df_base


  #
  # 詳細表示
  #
  def show_detail():

    # **********************************
    # 詳細画面
    # **********************************
    #
    # 閉じる
    #
    def close_detail_view():
      view_detail.destroy()

    # ★バグ対応用の関数を追加
    def fixed_map(option):
      return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]

    # --------------------
    # 詳細検索
    # --------------------
    item = table_result.item(table_result.selection(), 'values')

    channel_name = item[0]
    post_name = item[1]
    post_date = item[2]

    # read
    detail_filename = os.path.join(const.export_dir, '_public/' + channel_name + '.xlsx')
    df_detail_all = pd.read_excel(detail_filename, index_col=[0], names=('no', 'post_icon', 'post_name', 'post_date', 'post_message', 'reply_icon', 'reply_name', 'reply_date', 'reply_message', 'group_flg'))
    df_detail_all['post_message'] = df_detail_all['post_message'].astype(str)
    df_detail_all['reply_message'] = df_detail_all['reply_message'].astype(str)

    # 絞り込み
    df_detail = (
        df_detail_all.query('post_name == "' + post_name +  '"')
        .query('post_date == "' + post_date +  '"')
        .sort_values(by=['reply_date'], ascending=[True])
    )


    # --------------------
    # 画面表示
    # --------------------
    view_detail = tk.Tk()
    view_detail.geometry(str(VIEW_RESULT_W) + 'x' + str(VIEW_RESULT_H))

    view_detail.title('詳細')

    view_detail.grid_columnconfigure(0, weight=2)
    view_detail.grid_columnconfigure(1, weight=2)
    view_detail.grid_columnconfigure(2, weight=2)
    view_detail.grid_columnconfigure(3, weight=2)
    view_detail.grid_columnconfigure(4, weight=1)
    view_detail.grid_rowconfigure(4, weight=1)

    # ボタンレイアウト
    frame_detail_btn = tk.Frame(view_detail, borderwidth=1, relief='groove')
    frame_detail_btn.grid(row=0, column=0, sticky=tk.W+tk.E, padx=10, pady=10)

    btn_detail_back = tk.Button(
        frame_detail_btn,
        text = '戻る',
        width = 10,
        command = close_detail_view
    )
    btn_detail_back.pack(side=tk.LEFT, padx=10, pady=10)


    # ヘッダレイアウト
    # channel
    frame_detail_header1 = tk.Frame(view_detail)
    frame_detail_header1.grid(row=1, column=0, sticky=tk.W+tk.E, padx=10, pady=10)

    label_channel_name = tk.Label(frame_detail_header1, width=10, text='cnannel')
    label_channel_name.pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=5)
    text_channel_name = tk.Entry(frame_detail_header1, width=50)
    text_channel_name.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=5)
    text_channel_name.insert('end', channel_name)
    text_channel_name.configure(state=tk.DISABLED)

    # 投稿者
    frame_detail_header2 = tk.Frame(view_detail)
    frame_detail_header2.grid(row=2, column=0, sticky=tk.W+tk.E, padx=10, pady=10)

    label_post_name = tk.Label(frame_detail_header2, width=10, text='投稿者')
    label_post_name.pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=5)
    text_post_name = tk.Entry(frame_detail_header2, width=50)
    text_post_name.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=5)
    text_post_name.insert('end', post_name)
    text_post_name.configure(state=tk.DISABLED)

    # メッセージ
    frame_detail_header3 = tk.Frame(view_detail)
    frame_detail_header3.grid(row=3, column=0, sticky=tk.W+tk.E, padx=10, pady=10)

    label_post_name = tk.Label(frame_detail_header3, width=10, text='メッセージ')
    label_post_name.pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=5)
    text_post_message = ScrolledText(
        frame_detail_header3,
        wrap='char',
        width=200,
        height=5
    )
    text_post_message.insert('end', df_detail.iloc[0, 4])
    text_post_message.configure(state=tk.DISABLED)
    text_post_message.pack(side=tk.LEFT, anchor=tk.W, padx=5, pady=5)


    # --------------------
    # 詳細表示
    # --------------------
    frame_detail = tk.Frame(view_detail, borderwidth=1, relief='groove')
    frame_detail.grid(row=4, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=10, pady=10)

    table_detail = ttk.Treeview(frame_detail)

    style_detail = ttk.Style(frame_detail)
    style_detail.configure('Treeview', rowheight=60)

    # ★バグ対応を処理
    style.map('Treeview', background=fixed_map('background'))

    table_detail['columns'] = (1, 2, 3)
    table_detail['show'] = 'headings'

    # 列幅の設定
    view_detail.update_idletasks()
    # FIXME:常に1が返ってくる
  #  frame_result_width = frame_result.winfo_width()
    frame_detail_width = FRAME_RESULT_W
    w_user_detail = int(frame_result_width * 0.1)
    w_date_detail = int(frame_result_width * 0.1)
    w_message_detail = int(frame_result_width * 0.7)
    table_detail.column(1, width=w_user_detail, anchor=tk.NW)
    table_detail.column(2, width=w_date_detail, anchor=tk.N)
    table_detail.column(3, width=w_message_detail, anchor=tk.NW)

    # 列名
    table_detail.heading(1, text='返信者')
    table_detail.heading(2, text='返信日')
    table_detail.heading(3, text='メッセージ')

    rows = len(df_detail)
    for i in range(rows):
      str_width = int(frame_detail_width * 0.1)
      reply_message = '\n'.join(textwrap.wrap(df_detail.iloc[i, 8], width=str_width))
      table_detail.insert('', 'end', tag=0, values=[df_detail.iloc[i, 6], df_detail.iloc[i, 7], reply_message], tags=i)

      if i & 1:
        # tagが奇数(レコードは偶数)の場合のみ、背景色の設定
        table_detail.tag_configure(i, background='#CCFFFF')

    vbar2 = ttk.Scrollbar(frame_detail, orient = 'v', command=table_detail.yview)

    table_detail.configure(yscrollcommand=vbar2.set)

    table_detail.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

    frame_detail.grid_columnconfigure(0, weight=1)
    frame_detail.grid_rowconfigure(0, weight=1)

    vbar2.grid(row=0, column=1, sticky=tk.N+tk.S)


  # --------------------
  # 検索
  # --------------------
  srch_list = text_srch_str.get().split()
  srch_user_list = []
  for i in range(len(val_poster)):
    if val_poster[i].get():
      srch_user_list.append(poster_list[i].split(',')[0].replace('\n', ''))

  srch_channel_list = []
  for i in range(len(val_channel)):
    if val_channel[i].get():
      srch_channel_list.append(channel_list[i].split(',')[0].replace('\n', ''))

  if len(srch_channel_list) == 0:
    # 全てチェックOFFの場合、全てを対象とする
    for i in range(len(val_channel)):
      srch_channel_list.append(channel_list[i].split(',')[0].replace('\n', ''))

  df_list = []
  for i in range(len(srch_channel_list)):
    # 検索
    df_list.append(search(srch_channel_list[i]))

  df_result = pd.concat(df_list).sort_values(by=['post_date', 'reply_date'], ascending=[True, True])

  # --------------------
  # 画面表示
  # --------------------
  view_result = tk.Tk()
  view_result.geometry(str(VIEW_RESULT_W) + 'x' + str(VIEW_RESULT_H))

  view_result.title('検索結果')

  # ボタンレイアウト
  view_result.grid_columnconfigure(0, weight=2)
  view_result.grid_columnconfigure(1, weight=1)
  view_result.grid_rowconfigure(1, weight=1)

  frame_result_btn = tk.Frame(view_result, borderwidth=1, relief='groove')
  frame_result_btn.grid(row=0, column=0, sticky=tk.W+tk.E, padx=10, pady=10)

  btn_result_back = tk.Button(
      frame_result_btn,
      text = '戻る',
      width = 10,
      command = close_result_view
  )
  btn_result_back.pack(side=tk.LEFT, padx=10, pady=10)

  btn_result_detail = tk.Button(
      frame_result_btn,
      text = '詳細表示',
      width = 10,
      command = show_detail
  )
  btn_result_detail.pack(side=tk.LEFT, padx=10, pady=10)

  # 検索結果
  frame_result = tk.Frame(view_result, borderwidth=1, relief='groove')
  frame_result.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=10, pady=10)

  table_result = ttk.Treeview(frame_result)

  style = ttk.Style(frame_result)
  style.configure('Treeview', rowheight=60)

  # ★バグ対応を処理
  style.map('Treeview', background=fixed_map('background'))

  table_result['columns'] = (1, 2, 3, 4, 5, 6, 7)
  table_result['show'] = ['tree', 'headings']

  # 列幅の設定
  view_result.update_idletasks()
  # FIXME:常に1が返ってくる
#  frame_result_width = frame_result.winfo_width()
  frame_result_width = FRAME_RESULT_W
  w_channel = int(frame_result_width * 0.1)
  w_user = int(frame_result_width * 0.05)
  w_date = int(frame_result_width * 0.1)
  w_message = int(frame_result_width * 0.3)
  table_result.column('#0', width=20, anchor=tk.NW)
  table_result.column(1, width=w_channel, anchor=tk.NW)
  table_result.column(2, width=w_user, anchor=tk.NW)
  table_result.column(3, width=w_date, anchor=tk.N)
  table_result.column(4, width=w_message, anchor=tk.NW)
  table_result.column(5, width=w_user, anchor=tk.NW)
  table_result.column(6, width=w_date, anchor=tk.N)
  table_result.column(7, width=w_message, anchor=tk.NW)

  # 列名
  table_result.heading('#0', text='')
  table_result.heading(1, text='channel')
  table_result.heading(2, text='投稿者')
  table_result.heading(3, text='投稿日')
  table_result.heading(4, text='メッセージ')
  table_result.heading(5, text='返信者')
  table_result.heading(6, text='返信日')
  table_result.heading(7, text='メッセージ')

  rows = len(df_result)
  bef_post_name = None
  bef_post_date = None
  for i in range( rows ):
    str_width = int(frame_result_width * 0.028)
    post_message = '\n'.join(textwrap.wrap(df_result.iloc[i, 4], width=str_width))
    reply_name = df_result.iloc[i, 6] if not df_result.iloc[i, 6] == 'nan' else ''
    reply_date = df_result.iloc[i, 7] if not df_result.iloc[i, 7] == 'nan' else ''
    reply_message = '\n'.join(textwrap.wrap(df_result.iloc[i, 8], width=str_width)) if not df_result.iloc[i, 8] == 'nan' else ''

    if bef_post_name == str(df_result.iloc[i, 2]) and bef_post_date == str(df_result.iloc[i, 3]):
      # 同一グループの場合、親IDをセット
      table_result.insert(parent_iid, 'end', tag=0, values=[df_result.iloc[i, 10], df_result.iloc[i, 2], df_result.iloc[i, 3], post_message, reply_name, reply_date, reply_message], tags=i)
    else:
      parent_iid = table_result.insert('', 'end', tag=0, values=[df_result.iloc[i, 10], df_result.iloc[i, 2], df_result.iloc[i, 3], post_message, reply_name, reply_date, reply_message], tags=i)
      bef_post_name = str(df_result.iloc[i, 2])
      bef_post_date = str(df_result.iloc[i, 3])


    if i & 1:
      # tagが奇数(レコードは偶数)の場合のみ、背景色の設定
      table_result.tag_configure(i, background='#CCFFFF')

  vbar1 = ttk.Scrollbar(frame_result, orient = 'v', command=table_result.yview)

  table_result.configure(yscrollcommand=vbar1.set)

  table_result.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

  frame_result.grid_columnconfigure(0, weight=1)
  frame_result.grid_rowconfigure(0, weight=1)

  vbar1.grid(row=0, column=1, sticky=tk.N+tk.S)

  view_result.mainloop()



view = tk.Tk()
view.geometry('800x500')

view.title('検索')

# ボタンバー
frame = tk.Frame(view, borderwidth=1, relief='groove')
frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=10)

# 閉じるボタン
btn_close = tk.Button(
    frame,
    text = '閉じる',
    width = 10,
    command = do_close
)
btn_close.pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=10)

# 検索条件フレーム
frame_srch_str = tk.Frame(view, borderwidth=1, relief='groove')
frame_srch_str.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# 検索文字
label_srch_str = tk.Label(frame_srch_str, text='検索文字')
#label_srch_str.place(x=X_SRCH_STR, y=Y_SRCH_STR)
label_srch_str.pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=10)

text_srch_str = tk.Entry(frame_srch_str, width=50)
#text_srch_str.place(x=X_SRCH_BOX, y=Y_SRCH_STR)
text_srch_str.pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=10)

# 検索タイプ
srch_type_list = ['AND検索', 'OR検索']
val_srch_type = tk.IntVar()

for i in range(len(srch_type_list)):
  tk.Radiobutton(
      frame_srch_str,
      value = i,
      variable = val_srch_type,
      text = srch_type_list[i]
  ).pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=10)

val_srch_type.set(0)

# 検索ボタン
btn_srch = tk.Button(
    frame_srch_str,
    text = '検索',
    width = 10,
    command = do_search
)
btn_srch.pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=10)

# メンバーフレーム
frame_member_title = tk.Frame(view, width=350)
frame_member_title.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
frame_member_list = tk.Frame(view, width=350, borderwidth=1, relief='groove')
frame_member_list.grid(row=4, column=0, sticky=tk.W, padx=10)

# 投稿者
val_all_chk_poster = tk.BooleanVar()
all_chk_poster = tk.Checkbutton(
    frame_member_title,
    variable = val_all_chk_poster,
    text = '投稿者/返信者',
    command = all_check_member_list
).pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=5)

with open(const.member_list) as f:
  poster_list = f.readlines()

#poster_list = ['hamada', 'genta', 'genta', 'genta', 'genta', 'genta']
val_poster = {}

row, column=0, 0
for i in range(len(poster_list)):
  if i % 10 == 0:
    row = 0
    column += 1
  else:
    row += 1

  member_name = poster_list[i].split(',')[0].replace('\n', '')
  default_chk = poster_list[i].split(',')[1].replace('\n', '')

  val_poster[i] = tk.BooleanVar()
  tk.Checkbutton(
      frame_member_list,
      variable = val_poster[i],
      text = member_name
  ).grid(row=row, column=column, sticky=tk.W, padx=10)

  if default_chk == '1':
    val_poster[i].set(True)


# メンバーフレーム
frame_channel_title = tk.Frame(view, width=350)
frame_channel_title.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
frame_channel_list = tk.Frame(view, width=350, borderwidth=1, relief='groove')
frame_channel_list.grid(row=4, column=1, sticky=tk.W, padx=10)

# channel
val_all_chk_channel = tk.BooleanVar()
all_chk_channel = tk.Checkbutton(
    frame_channel_title,
    variable = val_all_chk_channel,
    text = 'channel',
    command = all_check_channel_list
).pack(side=tk.LEFT, anchor=tk.W, padx=10, pady=5)


with open(const.channel_list) as f:
  channel_list = f.readlines()

val_channel = {}

row, column=0, 0
for i in range(len(channel_list)):
  if i % 10 == 0:
    row = 0
    column += 1
  else:
    row += 1

  channel_name = channel_list[i].split(',')[0].replace('\n', '')
  default_chk = channel_list[i].split(',')[1].replace('\n', '')

  val_channel[i] = tk.BooleanVar()
  tk.Checkbutton(
      frame_channel_list,
      variable = val_channel[i],
      text = channel_name
  ).grid(row=row, column=column, sticky=tk.W, padx=10)

  if default_chk == '1':
    val_channel[i].set(True)


view.mainloop()



