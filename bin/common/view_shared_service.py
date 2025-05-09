"""
画面系共通サービス

create 2024/02/22 TIS hamada
"""
import tkinter as tk
import tkinter.ttk as ttk

LABEL_BG = '#4169e1'
LABEL_FG = 'white'


def create_label(root, label_name, width=6):
    """
    ラベル作成

    Args:
        root:
        label_name:
        width:

    Returns:

    """
    return tk.Label(root, text=label_name, width=width, foreground=LABEL_FG, background=LABEL_BG)


def create_entry(root, width=40):
    """
    テキストボックス作成

    Args:
        root:
        width:

    Returns:

    """
    return tk.Entry(root, width=width)


def create_checkbox(root, checkbox_name):
    """
    チェックボックス作成

    Args:
        root:
        checkbox_name:

    Returns:

    """
    var = tk.BooleanVar()
    checkbox = tk.Checkbutton(root, text=checkbox_name, variable=var, background=LABEL_FG)
    return checkbox, var


def pack_frame(root):
    """
    フレーム配置

    Returns:

    """
    frame = tk.Frame(root)
    frame.config(bg='white')
    frame.pack(side='top', anchor=tk.W, pady=15, padx=150)
    return frame


def pack_label(root, label_name, width=6):
    """
    ラベル配置

    Args:
        root:
        label_name:
        width:

    Returns:

    """
    label = create_label(root, label_name, width)
    label.pack(side='left', padx=5)
    return label


def pack_entry(root, width=40):
    """
    テキストボックス配置

    Args:
        root:
        width:

    Returns:

    """
    entry = create_entry(root, width)
    entry.pack(side='left', padx=5)
    return entry


def pack_checkbox(root, checkbox_name):
    """
    チェックボックス配置

    Args:
        root:
        checkbox_name:

    Returns:

    """
    checkbox, var = create_checkbox(root, checkbox_name)
    checkbox.pack(side='left', padx=5)
    return checkbox, var


def pack_button(root, button_name, width=9, is_leftmost=True):
    """
    ボタン配置

    Args:
        root:
        button_name:
        width:
        is_leftmost:

    Returns:

    """
    button = tk.Button(root, text=button_name, width=width)
    if is_leftmost:
        button.pack(side='left')
    else:
        button.pack(side='left', padx=10)
    return button


def set_readonly(obj):
    """
    tkinterオブジェクトをreadonlyに設定

    Args:
        obj:

    Returns:

    """
    obj.configure(state='readonly', readonlybackground='gray')


def set_combobox_style():
    """
    コンボボックススタイルを設定

    Returns:

    """
    style = ttk.Style()
    style.map(
        'TCombobox',
        fieldbackground=[
            ('readonly', '!focus', 'white'),
            ('readonly', 'focus', 'white')
        ],
        selectbackground=[
            ('readonly', '!focus', 'white'),
            ('readonly', 'focus', 'white')
        ],
        selectforeground=[
            ('readonly', '!focus', 'black'),
            ('readonly', 'focus', 'black')
        ]
    )


def set_treeview_style():
    """
    Treeviewのスタイルを設定

    Returns:

    """
    style = ttk.Style()
    style.theme_use('default')
    style.map('Treeview')
    style.configure('Treeview.Heading', background='#ff7f50')
