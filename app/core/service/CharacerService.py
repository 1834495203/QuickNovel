import base64
import re
from uuid import uuid4
import jsonlines
from typing import List, Optional

from fastapi import UploadFile

from core.entity.CharacterCard import CharacterCard
from core.entity.ResponseEntity import ResponseModel, success, error
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = f"{CURRENT_DIR}/../../static"
db_path = f'{CURRENT_DIR}/db/characters.jsonl'

def load_all_characters() -> ResponseModel[List[CharacterCard]]:
    try:
        with jsonlines.open(db_path) as reader:
            characters = [CharacterCard(**obj) for obj in reader]
            return success(data=characters, message="角色列表获取成功")
    except Exception as e:
        return error(message=f"获取角色列表失败: {str(e)}")

def get_id() -> ResponseModel:
    try:
        id = len(load_all_characters().data or []) + 1
        return success(data=id, message="ID生成成功")
    except Exception as e:
        return error(message=f"ID生成失败: {str(e)}")

def save_all_characters(characters: List[CharacterCard]) -> ResponseModel:
    try:
        with jsonlines.open(db_path, mode='w') as writer:
            writer.write_all([char.model_dump() for char in characters])
        return success(message="保存成功")
    except Exception as e:
        return error(message=f"保存失败: {str(e)}")

def upload_image(base64_string: str) -> ResponseModel:
    """处理图像上传并返回相对路径"""
    try:
        # 解析 base64 字符串
        match = re.match(r"data:image/(\w+);base64,(.+)", base64_string)
        if not match:
            return error(message="无效的图片格式")

        file_extension = match.group(1).lower()
        image_data = match.group(2)

        # 验证文件类型
        if file_extension not in ["jpg", "jpeg", "png", "gif"]:
            return error(message="不支持的文件格式，仅支持 jpg、jpeg、png、gif")

        # 解码 base64 数据
        image_data = base64.b64decode(image_data)

        # 生成唯一文件名
        unique_filename = f"{uuid4()}.{file_extension}"
        avatar_path = f"avatars/{unique_filename}"
        file_path = os.path.join(STATIC_DIR, avatar_path)

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 保存图片
        with open(file_path, 'wb') as buffer:
            buffer.write(image_data)

        return success(data=avatar_path, message="图片上传成功")
    except Exception as e:
        return error(message=f"处理图片失败: {str(e)}")

def add_character(card: CharacterCard) -> ResponseModel:
    try:
        # 加载现有角色
        characters = load_all_characters().data or []
        if any(c.id == card.id for c in characters):
            return error(message=f"角色 ID {card.id} 已存在")

        # 处理图片
        if card.avatar and card.avatar.startswith("data:image/"):
            upload_result = upload_image(card.avatar)
            if upload_result.code != 200:
                return upload_result
            card.avatar = upload_result.data

        # 添加角色到列表
        characters.append(card)
        save_result = save_all_characters(characters)
        if save_result.code != 200:
            return save_result

        return success(message="角色添加成功")
    except Exception as e:
        return error(message=f"添加角色失败: {str(e)}")

def get_character_by_id(character_id: int) -> ResponseModel[Optional[CharacterCard]]:
    try:
        characters = load_all_characters().data or []
        for c in characters:
            if c.id == character_id:
                return success(data=c, message="角色获取成功")
        return error(message=f"未找到ID为 {character_id} 的角色")
    except Exception as e:
        return error(message=f"获取角色失败: {str(e)}")

def update_character(character_id: int, updated_card: CharacterCard, upload_file: Optional[UploadFile] = None) -> ResponseModel:
    try:
        characters = load_all_characters().data or []
        updated = False

        for i, c in enumerate(characters):
            if c.id == character_id:
                # 保存旧头像路径
                old_avatar = c.avatar

                # 处理头像
                if upload_file is not None:
                    # 验证文件类型
                    file_extension = upload_file.filename.split('.')[-1].lower()
                    if file_extension not in ["jpg", "jpeg", "png", "gif"]:
                        return error(message="不支持的文件格式，仅支持 jpg、jpeg、png、gif")

                    # 生成唯一文件名
                    unique_filename = f"{uuid4()}.{file_extension}"
                    avatar_path = f"avatars/{unique_filename}"
                    file_path = os.path.join(STATIC_DIR, avatar_path)

                    # 确保目录存在
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # 保存新图片
                    with open(file_path, 'wb') as buffer:
                        buffer.write(upload_file.file.read())

                    # 更新头像路径
                    updated_card.avatar = avatar_path

                    # 删除旧头像文件（如果存在）
                    if old_avatar and os.path.exists(os.path.join(STATIC_DIR, old_avatar)):
                        try:
                            os.remove(os.path.join(STATIC_DIR, old_avatar))
                        except Exception as e:
                            return error(message=f"删除旧头像失败: {str(e)}")
                else:
                    # 保留原头像
                    updated_card.avatar = c.avatar

                characters[i] = updated_card
                updated = True
                break

        if not updated:
            return error(message=f"角色 ID {character_id} 不存在")

        save_result = save_all_characters(characters)
        if save_result.code != 200:
            return save_result
        return success(message="角色更新成功")
    except Exception as e:
        return error(message=f"更新角色失败: {str(e)}")

def delete_character(character_id: int) -> ResponseModel:
    try:
        characters = load_all_characters().data or []
        new_characters = []
        avatar_to_delete = None

        for c in characters:
            if c.id == character_id:
                # 记录需要删除的头像路径
                if c.avatar and os.path.exists(os.path.join(STATIC_DIR, c.avatar)):
                    avatar_to_delete = c.avatar
                continue
            new_characters.append(c)

        if len(new_characters) == len(characters):
            return error(message=f"角色 ID {character_id} 不存在")

        # 保存新角色列表
        save_result = save_all_characters(new_characters)
        if save_result.code != 200:
            return save_result

        # 删除头像文件
        if avatar_to_delete:
            try:
                os.remove(os.path.join(STATIC_DIR, avatar_to_delete))
            except Exception as e:
                return error(message=f"删除头像文件失败: {str(e)}")

        return success(message="角色删除成功")
    except Exception as e:
        return error(message=f"删除角色失败: {str(e)}")