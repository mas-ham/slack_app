"""
Loggerクラス

create 2023/05/13 TIS hamada
"""
import os
import datetime
import getpass

from common.logger.base_logger import BaseLogger

EXCEPTION_DIR = 'exception'
EXCEPTION_FILENAME_PREFIX = 'exception_'
LOG_LEVELS = {'DEBUG': 10, 'INFO': 20, 'WARN': 30, 'ERROR': 40, 'FATAL': 50}


class Logger(BaseLogger):
    def __init__(self, log_dir, log_filename='app.log', encoding='utf-8', log_level='INFO'):
        super().__init__(log_dir)

        self.log_filename = log_filename
        self.encoding = encoding
        self.log_level = log_level

        # 初期化
        self.__init_log()


    def __init_log(self):
        """
        ログファイル初期化

        Returns:

        """
        # ログローテート
        self.log_rotate(self.log_filename)


    def write_log(self, log_type, *args, is_print=True):
        """
        ログ出力

        Args:
            log_type:
            args:
            is_print:

        Returns:

        """
        # ログ出力
        if LOG_LEVELS[log_type] < self.get_log_level(self.log_level):
            return

        # ログファイル
        log_file = os.path.join(self.log_dir, self.log_filename)
        # 時間
        log_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # ログファイル書き込み
        with open(log_file, 'a', encoding=self.encoding) as f:
            log_message = ''
            for arg in args:
                if type(arg) == tuple:
                    log_message = '(' + '  '.join([s for s in arg]) + ')'
                elif type(arg) == list:
                    log_message = '[' + '  '.join(arg) + ']'
                else:
                    log_message = str(arg)
            f.write(f'[{log_time}] [{log_type}] {log_message}\n')

        #* コンソール出力
        if is_print:
            print(log_message)


    def debug(self, *args, is_print=True):
        """
        ログ出力:DEBUG

        Args:
            args:
            is_print:

        Returns:

        """
        self.write_log('DEBUG', *args, is_print=is_print)


    def info(self, *args, is_print=False):
        """
        ログ出力:INFO

        Args:
            args:
            is_print:

        Returns:

        """
        self.write_log('INFO', *args, is_print=is_print)


    def warn(self, *args, is_print=False):
        """
        ログ出力:WARN

        Args:
            args:
            is_print:

        Returns:

        """
        self.write_log('WARN', *args, is_print=is_print)


    def error(self, *args, is_print=True):
        """
        ログ出力:ERROR

        Args:
            args:
            is_print:

        Returns:

        """
        self.write_log('ERROR', *args, is_print=is_print)


    def fatal(self, *args, is_print=True):
        """
        ログ出力:FATAL

        Args:
            args:
            is_print:

        Returns:

        """
        self.write_log('FATAL', *args, is_print=is_print)


    def write_exception_log(self, log_message):
        """
        Exception出力

        Args:
            log_message:

        Returns:

        """
        # Exceptionログファイル名を組み立て
        user_id = getpass.getuser()
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = EXCEPTION_FILENAME_PREFIX + f'{now}_{user_id}.log'

        # ログディレクトリ
        log_dir = os.path.join(self.log_dir, EXCEPTION_DIR)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)

        # ログファイル
        log_file = os.path.join(log_dir, log_filename)
        # 時間
        log_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # ログファイル書き込み
        with open(log_file, 'a', encoding=self.encoding) as f:
            f.write(f'[{log_time}]\n' + log_message + '\n')


    def delete_log(self):
        """
        ログファイル削除

        Returns:

        """
        self.execute_delete_log(self.log_filename)


