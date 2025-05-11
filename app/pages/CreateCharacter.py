import streamlit as st
import pandas as pd
import datetime

from core.entity.CharacterCard import *
from core.service.CharacerService import *

# 设置保存图片的目录
SAVE_DIR = "./static"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Streamlit 应用界面
st.title("角色卡信息填写")

# 使用 st.form 来组织输入，提交时一次性处理
with st.form("character_card_form"):
    st.header("基础信息")
    # SimpleCharacterCard 字段

    # 图片上传
    avatar_path = None
    # 创建两列布局
    col1, col2 = st.columns([1, 1])  # 左右各占一半宽度
    with col2:
        # 右列：上传组件
        uploaded_file = st.file_uploader("上传头像", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            # 生成唯一文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = uploaded_file.name
            new_filename = f"avatar_{timestamp}_{original_filename}"
            avatar_path = os.path.join(SAVE_DIR, new_filename)

            # 保存图片到 ./static
            with open(avatar_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success("图片上传并保存成功！")

    with col1:
        # 左列：显示图片（占位或上传后的图片）
        if uploaded_file is not None:
            st.image(avatar_path, caption="上传的头像", width=200)
        else:
            st.write("头像预览")
            st.image("./static/header.png", caption="默认头像", width=200)  # 占位图

    name = st.text_input("角色名称 ")
    description = st.text_area("角色描述", placeholder="在这里描述角色的年龄，性别，职业等信息")

    st.header("背景")
    # Background - background_story
    background_story = st.text_area("角色出身 (选填)")

    st.header("性格")
    st.write("填写性格特征列表:")
    # Personality - traits (使用 data_editor)
    traits_data = st.data_editor(
        pd.DataFrame([{"label": "", "description": ""}]), # 初始数据
        num_rows="dynamic", # 允许动态增删行
        column_config={
            "label": st.column_config.TextColumn("特征标签", required=True),
            "description": st.column_config.TextColumn("特征描述", required=True),
        },
        hide_index=True
    )

    st.header("行为")
    st.write("填写说话方式示例:")
    # Behaviors - speakingStyle (使用 data_editor)
    speaking_style_data = st.data_editor(
        pd.DataFrame([{"role": "", "content": "", "reply": ""}]), # 初始数据
        num_rows="dynamic",
        column_config={
            "role": st.column_config.TextColumn("询问的人", required=True),
            "content": st.column_config.TextColumn("台词", required=True),
            "reply": st.column_config.TextColumn("角色回复示例", required=True),
        },
        hide_index=True
    )

    st.header("能力和专长")
    st.write("填写知识领域和兴趣爱好:")
    # Abilities - knowledge (使用 data_editor)
    knowledge_data = st.data_editor(
        pd.DataFrame([{"知识领域": "", "兴趣爱好": ""}]),  # 初始数据
        num_rows="dynamic",
        column_config={
            "知识领域": st.column_config.TextColumn("知识领域", required=True),
            "兴趣爱好": st.column_config.TextColumn("兴趣爱好", required=True),
        },
        hide_index=True
    )

    st.header("用户自定义字段")
    st.write("填写自定义字段:")
    # CustomizeFields - fields (使用 data_editor)
    customize_fields_data = st.data_editor(
        pd.DataFrame([{"fieldName": "", "fieldValue": ""}]), # 初始数据
        num_rows="dynamic",
        column_config={
            "fieldName": st.column_config.TextColumn("字段名称", required=True),
            "fieldValue": st.column_config.TextColumn("字段值", required=True),
        },
        hide_index=True
    )

    # 提交按钮
    submitted = st.form_submit_button("生成角色卡")

# 处理提交的数据
if submitted:
    try:
        # 转换 data_editor 的数据为 Pydantic 模型所需的格式
        traits_list = [Trait(**row) for row in traits_data.to_dict(orient='records') if row.get("label") and row.get("description")]
        speaking_style_list = [Speaking(**row) for row in speaking_style_data.to_dict(orient='records') if row.get("role") and row.get("content") and row.get("reply")]
        knowledge_list = [row["知识领域"] for row in knowledge_data.to_dict(orient='records') if row.get("知识领域")]
        hobby_list = [row["兴趣爱好"] for row in knowledge_data.to_dict(orient='records') if row.get("兴趣爱好")]
        customize_fields_list = [Distinctive(**row) for row in customize_fields_data.to_dict(orient='records') if row.get("fieldName") and row.get("fieldValue")]

        # 构建 Pydantic 模型实例
        simple_card = SimpleCharacterCard(
            id=get_id(),
            avatar=avatar_path if avatar_path else None,
            name=name if name else None,
            description=description if description else None,
        )

        personality_obj = Personality(traits=traits_list) if traits_list else None
        background_obj = Background(background_story=background_story) if background_story else None
        behaviors_obj = Behaviors(speakingStyle=speaking_style_list) if speaking_style_list else None
        abilities_obj = Abilities(knowledge=knowledge_list, hobby=hobby_list) if knowledge_list or hobby_list else None
        customize_obj = CustomizeFields(fields=customize_fields_list) if customize_fields_list else None

        character_card = CharacterCard(
            **simple_card.model_dump(exclude_none=True),  # 使用 model_dump 并排除 None 值
            personality=personality_obj,
            background=background_obj,
            behaviors=behaviors_obj,
            abilities=abilities_obj,
            customize=customize_obj,
        )

        st.success("角色卡数据已生成:")
        st.json(character_card.model_dump_json(indent=2))  # 显示生成的 JSON 数据
        add_character(card=character_card)

    except Exception as e:
        st.error(f"生成角色卡时出错: {e}")

