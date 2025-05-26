import json
import os
from enum import Enum
from typing import List, Dict, Any, Union

from pydantic import BaseModel


class JSONLStorage:
    """JSONL文件存储基础类"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                pass

    def read_all(self) -> List[Any]:
        """读取所有数据"""
        data = []
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            item = json.loads(line)
                            data.append(item)
                        except json.JSONDecodeError:
                            continue
        return data

    def write_all(self, data: List[Union[BaseModel, Dict[str, Any]]]):
        """写入所有数据"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            for item in data:
                if isinstance(item, BaseModel):
                    f.write(item.model_dump_json() + '\n')
                else:
                    # 兼容dict格式，处理enum序列化
                    serialized_item = {}
                    for k, v in item.items():
                        if isinstance(v, Enum):
                            serialized_item[k] = v.value
                        else:
                            serialized_item[k] = v
                    f.write(json.dumps(serialized_item, ensure_ascii=False) + '\n')

    def append(self, item: Union[BaseModel, Dict[str, Any]]):
        """追加单条数据"""
        with open(self.file_path, 'a', encoding='utf-8') as f:
            if isinstance(item, BaseModel):
                f.write(item.model_dump_json() + '\n')
            else:
                # 兼容dict格式，处理enum序列化
                serialized_item = {}
                for k, v in item.items():
                    if isinstance(v, Enum):
                        serialized_item[k] = v.value
                    else:
                        serialized_item[k] = v
                f.write(json.dumps(serialized_item, ensure_ascii=False) + '\n')