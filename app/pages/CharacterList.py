import streamlit as st
from pydantic import BaseModel
from typing import Optional
from PIL import Image
from core.service.CharacerService import *


# 定义 SimpleCharacterCard 模型
class SimpleCharacterCard(BaseModel):
    id: int  # 必填：角色唯一标识符
    avatar: Optional[str] = None  # 选填：头像链接
    name: Optional[str] = None  # 选填：角色名称
    description: Optional[str] = None  # 描述角色，重要


# 示例数据
characters = load_all_characters()

# Streamlit 页面设置
st.set_page_config(page_title="角色信息展示", layout="wide")

# 页面标题
st.title("角色信息展示")


# 模拟卡片效果的函数
def display_character_card(character):
    with st.container():
        # 使用 expander 模拟卡片效果，添加边框
        with st.expander("", expanded=True):
            col1, col2 = st.columns([1, 3])  # 头像占1，内容占3

            # 显示头像或占位
            with col1:
                if character.avatar:
                    st.image(character.avatar, width=200)
                else:
                    st.image('static/header.png', width=200)

            # 显示名称和描述
            with col2:
                st.subheader(character.name or "未命名角色")
                st.write(character.description or "暂无描述")

                # 操作按钮
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("编辑", key=f"edit_{character.id}"):
                        st.write(f"正在编辑角色 {character.name or 'ID ' + str(character.id)}")
                with btn_col2:
                    if st.button("删除", key=f"delete_{character.id}"):
                        st.write(f"正在删除角色 {character.name or 'ID ' + str(character.id)}")
                with btn_col3:
                    if st.button("查看详情", key=f"view_{character.id}"):
                        st.write(f"查看角色 {character.name or 'ID ' + str(character.id)} 的详细信息")


# 遍历角色并展示
for character in characters:
    display_character_card(character)