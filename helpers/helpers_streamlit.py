from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

def add_history_model(messages_list: list, chat_history: object, key: str) -> None:
    messages = []
    for message in messages_list:
        match message["role"]:
            case "user":
                messages.append(HumanMessage(content=message["message"]))
            case "model":
                messages.append(AIMessage(content=message["message"]))
    chat_history(key=key).add_messages(messages)
    

def get_chat_name(chat_list: list, text_input) -> None:
    chat_name = text_input
    chat_list.append(chat_name)
    text_input = ""
            

def format_messages_to_db(history: object) -> list:
    messages_list = []
    for msg in history.messages:
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