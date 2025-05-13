"""
OrderBy設定モデル

create 2024/03/29 TIS hamada
"""
import dataclasses


@dataclasses.dataclass
class OrderBy:
    key = None
    is_desc = False

    def __init__(self, key, is_desc = False):
        self.key = key
        self.is_desc = is_desc
