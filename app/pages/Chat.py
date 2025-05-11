import streamlit as st
from core.providers.Deepseek import DeepSeekChat
from core.providers.ProvidersBase import AbstractChat
from core.entity.Models import ChatContent
from datetime import datetime

# 侧边栏：配置系统提示词和清空历史
st.sidebar.header("设置")
system_prompt = st.sidebar.text_area("系统提示词（可选）", value="你是一个友好的助手，回答要简洁明了。始终用中文回答。")
if st.sidebar.button("清空聊天历史"):
    st.session_state.messages = []
    st.session_state.chat.clear_chat_history()
    st.rerun()

# 初始化会话状态和 DeepSeekChat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = DeepSeekChat(model="deepseek-chat")

chat: AbstractChat = st.session_state.chat

# 侧边栏：添加新消息
st.sidebar.header("添加新消息")
new_message_role = st.sidebar.selectbox("消息角色", ["user", "assistant", "system"])
new_message_content = st.sidebar.text_area("消息内容")
if st.sidebar.button("添加消息"):
    if new_message_content.strip():
        new_message = ChatContent(
            role=new_message_role,
            content=new_message_content,
            create_time=datetime.now()  # 添加时间戳
        )
        st.session_state.messages.append(new_message)
        chat.chat.set_message(new_message)
        st.rerun()

# 显示聊天历史
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message.role):
        # 显示楼层和时间
        timestamp = message.timestamp if hasattr(message, 'timestamp') else datetime.now()
        st.caption(f"楼层 #{index} | 发送时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # 显示消息内容（支持编辑）
        edit_key = f"edit_{index}_{message.role}"
        if edit_key in st.session_state and st.session_state[edit_key]:
            new_content = st.text_area("编辑消息", value=message.content, key=f"edit_area_{index}")
            if st.button("保存", key=f"save_{index}"):
                message.content = new_content
                st.session_state[edit_key] = False
                st.rerun()
            if st.button("取消", key=f"cancel_{index}"):
                st.session_state[edit_key] = False
                st.rerun()
        else:
            st.markdown(message.content)

        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("修改", key=f"modify_{index}"):
                st.session_state[edit_key] = True
                st.rerun()
        with col2:
            if st.button("删除", key=f"delete_{index}"):
                st.session_state.messages.pop(index - 1)
                st.rerun()

# 处理用户输入（通过聊天输入框，调用 LLM）
if prompt := st.chat_input("请输入消息..."):
    user_input = ChatContent(
        role="user",
        content=prompt,
        create_time=datetime.now()
    )
    st.session_state.messages.append(user_input)
    with st.chat_message("user"):
        st.caption(
            f"楼层 #{len(st.session_state.messages)} | 发送时间: {user_input.create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(prompt)

    # 调用 LLM API（流式模式）
    try:
        with st.chat_message("assistant"):
            # 准备消息并调用 API
            api_messages = chat.prepare_messages(prompt, system_prompt)
            response = chat.call_api(api_messages, stream=True)

            resp = st.write_stream(response)

            # 将最终响应添加到聊天历史
            assistant_message = ChatContent(
                role="assistant",
                content=resp,
                create_time=datetime.now()
            )
            st.session_state.messages.append(assistant_message)
            chat.chat.set_message(assistant_message)

    except Exception as e:
        st.error(f"API 调用失败: {str(e)}")
