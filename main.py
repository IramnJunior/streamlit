import streamlit as st
from streamlit_option_menu import option_menu

from langchain_community.utilities import SQLDatabase
from langchain_community.chat_message_histories import (
   StreamlitChatMessageHistory
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from database import delete_in_database, update_in_database, get_history

from dotenv import load_dotenv

load_dotenv()

import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")


if "chat_list" not in st.session_state:
    st.session_state.chat_list = []
    
if "messages_list" not in st.session_state:
    st.session_state.messages_list = []

if "disabled" not in st.session_state:
    st.session_state.disabled = True

if "chat_key" not in st.session_state:
    st.session_state.chat_key = "Chat 1"
    


def format_messages_list(messages_list: list):
    messages = []    
    for message in messages_list:
        match message["role"]:
            case "user":
                messages.append(HumanMessage(content=message["message"]))
            case "model":
                messages.append(AIMessage(content=message["message"]))
                
    msgs = StreamlitChatMessageHistory(key=st.session_state.chat_list[-1])        
    msgs.add_messages(messages)


if not st.session_state.chat_list:
    history = get_history()

    for chats in history:
        st.session_state.chat_list.append(chats.chat_name)
        
        chat_messages = chats.chat_messages["messages"]

        format_messages_list(chat_messages)



def get_chat_name():
    chat_name = st.session_state["text"]
    st.session_state.chat_list.append(chat_name)
    st.session_state["text"] = ""


def get_chat_selection(key):
    st.session_state.chat_key = st.session_state[key]


def list_messages():
    messages_list = []
    for msg in msgs.messages:
        match msg.type:
            case "human":
                messages_list.append({
                    "role": "user",
                    "message": msg.content
                })
            case "ai":
                messages_list.append({
                    "role": "model",
                    "message": msg.content
                })
    return messages_list


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
            delete_in_database(chat_name)
            
            

    text_input = st.text_input(label="Nome do novo chat",
                               key="text",
                               disabled=st.session_state.disabled,
                               on_change=get_chat_name,
                               args=None)
    
    
    if st.session_state.chat_list:
        selected = option_menu("Histórico", st.session_state.chat_list,
                               on_change=get_chat_selection, key="chats", 
                               styles={"container": {"background-color": "rgb(38, 39, 48)"},
                                       "nav-item": {"padding": "5px 0 5px"},         
                                       "icon": {"visibility": "hidden", "font-size": "0px"},
                                       })


db = SQLDatabase.from_uri("mysql+mysqldb://root:admin@localhost:3306/empresa_inseminacao")



prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Voce sera um chatbot em conversa com um humano. Fale somente em Portugues"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]
)

chain = prompt | llm

chain_with_history = RunnableWithMessageHistory(chain, lambda session_id: msgs,
                                                input_messages_key="question",
                                                history_messages_key="history",)

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt := st.chat_input():
    st.chat_message("human").markdown(prompt)
    
    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").markdown(response.content)
    
    update_in_database(st.session_state.chat_key, {"messages": list_messages()})