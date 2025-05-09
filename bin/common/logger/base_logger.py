"""
Logger基底クラス

create 2024/04/20 TIS hamada
"""
import os
import datetime
import pathlib
import shutil

LOG_LEVELS = {'DEBUG': 10, 'INFO': 20, 'WARN': 30, 'ERROR': 40, 'FATAL': 50}


class BaseLogger:
    def __init__(self, log_dir, encoding='utf-8'):
        self.log_dir = log_dir
        self.encoding = encoding

        if not os.path.isdir(self.log_dir):
            os.makedirs(self.log_dir)


    def log_rotate(self, target_log_filename):
        """
        ログローテート

        Args:
            target_log_filename:

        Returns:

        """
        try:
            # 既存ログファイルの更新日を取得
            target_log_file = os.path.join(self.log_dir, target_log_filename)
            p = pathlib.Path(target_log_file)
            mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime)

            if not datetime.datetime.today().strftime('%Y%d%m') == mtime.strftime('%Y%d%m'):
                # ログローテート
                suffix = datetime.datetime.strftime(mtime, '%Y-%m-%d')
                rotate_log_dir = os.path.join(self.log_dir, 'rotate')
                rotate_log_file = os.path.join(rotate_log_dir, target_log_filename + '.' + suffix)
                # フォルダ作成
                if not os.path.isdir(rotate_log_dir):
                    os.makedirs(rotate_log_dir)
                # ローテートフォルダへ移動
                shutil.move(target_log_file, rotate_log_file)

        except:
            return


    def execute_delete_log(self, target_filename):
        """
        ログファイル削除

        Returns:

        """
        # ログファイル
        log_file = os.path.join(self.log_dir, target_filename)
        if os.path.exists(log_file):
            os.remove(log_file)


    @classmethod
    def get_log_level(cls, log_level):
        """
        ログ出力レベルを取得

        Returns:

        """
        try:
            return LOG_LEVELS[log_level]
        except:
            #! エラー時は全レベル出力する
            return 0
