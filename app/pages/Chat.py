import streamlit as st

from core.providers.Deepseek import DeepSeekChat
from core.providers.ProvidersBase import AbstractChat
from core.entity.Models import ChatContent

if __name__ == "__main__":
    # 侧边栏：配置系统提示词和清空历史
    st.sidebar.header("设置")
    system_prompt = st.sidebar.text_area("系统提示词（可选）", value="你是一个友好的助手，回答要简洁明了。始终用中文回答。")
    if st.sidebar.button("清空聊天历史"):
        st.session_state.messages = []
        st.session_state.chat.clear_chat_history()
        st.rerun()

    # 初始化会话状态和 OpenAIChat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat" not in st.session_state:
        st.session_state.chat = DeepSeekChat(model="deepseek-chat")

    chat: AbstractChat = st.session_state.chat

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)

    # 处理用户输入
    if prompt := st.chat_input("What is up?"):
        user_input = ChatContent(role="user", content=prompt)
        st.session_state.messages.append(user_input)
        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用 LLM API（流式模式）
        try:
            with st.chat_message("assistant"):
                # 准备消息并调用 API
                api_messages = chat.prepare_messages(prompt, system_prompt)
                response = chat.call_api(api_messages, stream=True)

                resp = st.write_stream(response)

                # 将最终响应添加到聊天历史
                assistant_message = ChatContent(role="assistant", content=resp)
                st.session_state.messages.append(assistant_message)
                chat.chat.set_message(assistant_message)

        except Exception as e:
            st.error(f"API 调用失败: {str(e)}")

