import streamlit as st
from streamlit_option_menu import option_menu

from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from llm import ( 
    chain,
    agent_executor
)

from structured_data import get_rag_response

from helpers.helpers_database import (
    update_in_db,
    delete_in_db,
    get_messages_db
)

from helpers.helpers_streamlit import (
    add_history_model,
    format_messages_to_db
)

if "chat_list" not in st.session_state:
    st.session_state.chat_list = []
    
if "messages_list" not in st.session_state:
    st.session_state.messages_list = []

if "disabled" not in st.session_state:
    st.session_state.disabled = True

if "chat_key" not in st.session_state:
    st.session_state.chat_key = "Chat 1"


if not st.session_state.chat_list:
    history = get_messages_db()
    
    print(history)

    for chats in history:
        
        print(chats.chat_name)
        
        st.session_state.chat_list.append(chats.chat_name)
        messages_list = chats.chat_messages["messages"]
        
        print(messages_list)
        
        add_history_model(
            messages_list=messages_list,
            chat_history=StreamlitChatMessageHistory,
            key=st.session_state.chat_list[-1]
        )

msgs = StreamlitChatMessageHistory(key=st.session_state.chat_key)

with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        if add_button := st.button("Criar novo chat"):
            st.session_state.disabled = False
        else:
            st.session_state.disabled = True
            
    with col2:
        if delete_button := st.button("Deletar chat"):
            msgs.clear()
            chat_name = st.session_state.chat_key           
            st.session_state.chat_list.remove(chat_name) 
            delete_in_db(chat_name)
    
    
    def get_chat_name():
        chat_name = st.session_state["text_input"]
        st.session_state.chat_list.append(chat_name)
        st.session_state["text_input"] = ""
            
    text_input = st.text_input(
        label="Nome do novo chat",
        key="text_input",
        disabled=st.session_state.disabled,
        on_change=get_chat_name,
        args=None
    )
    
    
    def get_chat_selection(key):
        st.session_state.chat_key = st.session_state[key]
    
    if st.session_state.chat_list:
        selected = option_menu(
            "Histórico", 
            st.session_state.chat_list,
            on_change=get_chat_selection, 
            key="chats",
            styles={
                "container": {"background-color": "rgb(38, 39, 48)"},        
                "icon": {"visibility": "hidden", "font-size": "0px"},
                "nav-item": {"padding": "5px 0 5px"},
            }
        )  

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt := st.chat_input():
    st.chat_message("human").markdown(prompt)
    config = {"configurable": {"session_id": "any"}}
    model_response = chain.invoke({"Context": "none", "question": prompt}, config)
    
    if "RAG" in model_response.content:
        model_response = get_rag_response(prompt)
        x = chain.invoke({"Context": model_response[0].page_content, "question": prompt}, config)
        print("rag response: ", model_response[0].page_content)
        response = x.content
    elif "SQL" in model_response.content:
        model_response = agent_executor.invoke(prompt)
        print(model_response["output"])
        response = model_response["output"]
    else:
        response = model_response.content
        
    st.chat_message("ai").markdown(response)
    
    msgs.add_user_message(prompt)
    msgs.add_ai_message(response)
    update_in_db(st.session_state.chat_key, {"messages": format_messages_to_db(msgs)})