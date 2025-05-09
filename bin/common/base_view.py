"""
UI基底クラス

create 2024/02/22 TIS hamada
"""
import tkinter as tk
import tkinter.ttk as ttk

LABEL_BG = '#4169e1'
LABEL_FG = 'white'

FRAME_PAD_X = (20, 20)
FRAME_PAD_Y = 10
DEFAULT_PAD_X = 5
DEFAULT_PAD_Y = 3


class BaseView(tk.Frame):
    """
    UI基底クラス
    """

    def __init__(self, bg='white', height=600, width=1500, master=None) -> None:
        super().__init__(master, bg=bg, height=height, width=width)


    @classmethod
    def create_frame(cls, root, bg='white'):
        """
        Frame生成

        Args:
            root:
            bg:

        Returns:

        """
        return tk.Frame(root, bg=bg)


    @classmethod
    def create_labelframe(cls, root, frame_name, height, width, bg='white'):
        """
        ラベルFrame生成

        Args:
            root:
            frame_name:
            height:
            width:
            bg:

        Returns:

        """
        frame = tk.LabelFrame(root, text=frame_name, height=height, width=width, bg=bg)
        frame.propagate(False)
        return frame


    @classmethod
    def grid_frame(cls, frame, row, column, rowspan=1, columnspan=1, sticky=tk.W+tk.E, padx=FRAME_PAD_X, pady=10):
        """
        Frame配置

        Args:
            frame:
            row:
            column:
            rowspan:
            columnspan:
            sticky:
            padx:
            pady:

        Returns:

        """
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)


    @classmethod
    def grid_label_th(cls, root, label_name, row, column, rowspan=1, columnspan=1, width=15, sticky=tk.W+tk.E, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y):
        """
        thラベル配置

        Args:
            root:
            label_name:
            row:
            column:
            rowspan:
            columnspan:
            width:
            sticky:
            padx:
            pady:

        Returns:

        """
        label = tk.Label(root, text=label_name, width=width, foreground=LABEL_FG, background=LABEL_BG)
        label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
        return label


    @classmethod
    def grid_label_td(cls, root, label_name, row, column, rowspan=1, columnspan=1, width=20, sticky=tk.W+tk.E, anchor=tk.W, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y):
        """
        tdラベル配置

        Args:
            root:
            label_name:
            row:
            column:
            rowspan:
            columnspan:
            width:
            sticky:
            anchor:
            padx:
            pady:

        Returns:

        """
        label = tk.Label(root, text=label_name, width=width, background='white', anchor=anchor)
        label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
        return label


    @classmethod
    def grid_label_variable(cls, root, textvariable, row, column, rowspan=1, columnspan=1, width=20, sticky=tk.W+tk.E, anchor=tk.W, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y):
        """
        動的ラベル配置

        Args:
            root:
            textvariable:
            row:
            column:
            rowspan:
            columnspan:
            width:
            sticky:
            anchor:
            padx:
            pady:

        Returns:

        """
        label = tk.Label(root, width=width, background='white', anchor=anchor, textvariable=textvariable)
        label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
        return label


    @classmethod
    def grid_entry(cls, root, row, column, rowspan=1, columnspan=1, width=40, sticky=tk.W+tk.E, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y, validate=None, validatecommand=None):
        """
        Entry配置

        Args:
            root:
            row:
            column:
            rowspan:
            columnspan:
            width:
            sticky:
            padx:
            pady:
            validate:
            validatecommand:

        Returns:

        """
        if validate is None:
            entry = tk.Entry(root, width=width)
        else:
            entry = tk.Entry(root, width=width, validate=validate, validatecommand=validatecommand)
        entry.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
        return entry


    @classmethod
    def grid_combobox(cls, root, values: list, row, column, rowspan=1, columnspan=1, height=5, width=40, justify='left', state='readonly', sticky=tk.W+tk.E, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y):
        """
        Combobox配置

        Args:
            root:
            values:
            row:
            column:
            rowspan:
            columnspan:
            height:
            width:
            justify:
            state:
            sticky:
            padx:
            pady:

        Returns:

        """
        combobox = ttk.Combobox(root, height=height, width=width, justify=justify, state=state, values=tuple(values))
        combobox.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
        return combobox


    @classmethod
    def grid_radiobutton(cls, root, text, variable, value, row, column, width=10, background = 'white', sticky=tk.W, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y):
        """
        Radiobutton配置

        Args:
            root:
            text:
            variable:
            value:
            row:
            column:
            width:
            background:
            sticky:
            padx:
            pady:

        Returns:

        """
        radiobutton = tk.Radiobutton(root, text=text, variable=variable, value=value, width=width, background=background)
        radiobutton.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)
        return radiobutton


    @classmethod
    def grid_checkbox(cls, root, text, row, column, width=10, background = 'white', sticky=tk.W, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y):
        """
        Checkbox配置

        Args:
            root:
            text:
            row:
            column:
            width:
            background:
            sticky:
            padx:
            pady:

        Returns:

        """
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(root, text=text, variable=var, width=width, background=background)
        checkbox.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)
        return checkbox, var


    @classmethod
    def create_treeview(cls, root, columns, height=15, selectmode='extended'):
        """
        TreeView生成

        Args:
            root:
            columns:
            height:
            selectmode:

        Returns:

        """
        return ttk.Treeview(root, columns=columns, height=height, selectmode=selectmode)


    @classmethod
    def grid_button(cls, root, button_name, row, column, width=9, sticky=tk.W, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y):
        """
        ボタン配置

        Args:
            root:
            button_name:
            row:
            column:
            width:
            sticky:
            padx:
            pady:

        Returns:

        """
        button = tk.Button(root, text=button_name, width=width)
        button.grid(row=row, column=column, sticky=sticky, padx=padx, pady=pady)
        return button


    @classmethod
    def add_scrollbar(cls, root, elem):
        """
        スクロールバー追加

        Args:
            root:
            elem:

        Returns:

        """
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=elem.yview)
        elem.configure(yscroll=scrollbar.set)

        elem.pack(side=tk.LEFT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    @classmethod
    def set_readonly(cls, obj):
        """
        tkinterオブジェクトをreadonlyに設定

        Args:
            obj:

        Returns:

        """
        obj.configure(state='readonly', readonlybackground='gray')


    @classmethod
    def set_combobox_style(cls):
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


    @classmethod
    def set_treeview_style(cls):
        """
        Treeviewのスタイルを設定

        Returns:

        """
        style = ttk.Style()
        style.theme_use('default')
        style.map('Treeview')
        style.configure('Treeview.Heading', background='#ff7f50')

