import shutil
import uuid
from pathlib import Path
from typing import List

from core.entity.ResponseEntity import ResponseModel, success, warning
from core.entity.dto.CharacterDto import CreateCharacterDto, ResponseCharacterDto
from core.mapper.CharacterMapper import CharacterMapperInterface


class CharacterService:

    def __init__(self, character_mapper: CharacterMapperInterface):
        self.character_mapper = character_mapper

        # 配置上传目录
        self.UPLOAD_DIR = Path("uploads/avatars")
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

    def validate_file_extension(self, filename: str) -> bool:
        """验证文件扩展名是否允许"""
        return Path(filename).suffix.lower() in self.ALLOWED_EXTENSIONS

    def create_character(self, character: CreateCharacterDto) -> ResponseModel:
        character_id = self.character_mapper.create_character(character)
        return success(f"创建角色成功, 角色id为{character_id}")

    def select_character_by_id(self, character_id: int) -> ResponseModel[ResponseCharacterDto]:
        character = self.character_mapper.select_character_by_id(character_id)
        return success(data=character, message="获取角色成功")

    def get_all_characters(self) -> ResponseModel[List[ResponseCharacterDto]]:
        characters = self.character_mapper.get_all_characters()
        return success(data=characters, message="获取全部角色成功")

    def delete_character(self, character_id: int) -> ResponseModel:
        is_delete = self.character_mapper.delete_character_by_id(character_id)
        if is_delete:
            return success(f"成功删除角色id为{character_id}的角色")
        return warning(message="删除角色id为{character_id}失败")

    def update_avatar(self, character_id: int, avatar_file) -> ResponseModel:
        # 验证文件扩展名
        if not self.validate_file_extension(avatar_file.filename):
            raise ValueError("不支持的文件格式，仅允许 PNG、JPG、JPEG")

        # 生成唯一文件名
        file_extension = Path(avatar_file.filename).suffix.lower()
        unique_filename = f"character_{character_id}_{uuid.uuid4()}{file_extension}"
        file_path = self.UPLOAD_DIR / unique_filename

        # 保存文件
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(avatar_file.file, buffer)
        except Exception as e:
            raise ValueError(f"文件保存失败: {str(e)}")

        avatar_name = f"uploads/avatars/{unique_filename}"

        is_update = self.character_mapper.update_avatar(character_id, avatar_name)
        if is_update:
            return success("上传头像成功")
        return warning(message="上传头像失败")
