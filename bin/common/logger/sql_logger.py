"""
Loggerクラス

create 2023/05/13 TIS hamada
"""
import os
import datetime

from common.logger.base_logger import BaseLogger


class SqlLogger(BaseLogger):
    def __init__(self, log_dir, sql_log_filename='sql.log', encoding='utf-8'):
        super().__init__(log_dir)

        self.sql_log_filename = sql_log_filename
        self.encoding = encoding

        # 初期化
        self.__init_log()


    def __init_log(self):
        """
        ログファイル初期化

        Returns:

        """
        # ログローテート
        self.log_rotate(self.sql_log_filename)


    def write_sql_log(self, func, sql, *args):
        """
        SQLログ出力

        Args:
            func:
            sql:
            *args:

        Returns:

        """
        # ログファイル
        log_file = os.path.join(self.log_dir, self.sql_log_filename)
        # 時間
        log_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # ログファイル書き込み
        with open(log_file, 'a', encoding=self.encoding) as f:
            sql_log = sql.replace('\n', ' ')
            f.write(f'[{log_time}] [{func}] Preparing: {sql_log}\n')
            param_list = []
            for arg in args:
                if type(arg) == tuple:
                    param_list.extend([self.__build_param_str(s) for s in arg])
                elif type(arg) == list:
                    param_list.extend([self.__build_param_str(s) for s in arg])
                else:
                    param_list.append(self.__build_param_str(arg))

            if param_list:
                f.write(f'[{log_time}] [{func}] Parameters: {", ".join(param_list)}\n')


    @classmethod
    def __build_param_str(cls, param):
        """
        SQLパラメーターログ用文字列の取得

        Args:
            param:

        Returns:

        """
        if type(param) == str:
            return f'{param}(String)'
        if type(param) == datetime:
            return f'{param}(Timestamp)'
        if type(param) == int:
            return f'{param}(Integer)'
        return param


    def delete_log(self):
        self.execute_delete_log(self.sql_log_filename)

