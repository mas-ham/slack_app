"""
検索条件設定モデル

create 2024/03/29 TIS hamada
"""
import dataclasses


@dataclasses.dataclass
class Condition:
    key = None
    val = None
    ope = ''

    def __init__(self, key = None, val = None, ope = ''):
        self.key = key
        self.val = val
        self.ope = ope
