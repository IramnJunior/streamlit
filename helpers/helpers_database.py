from sqlalchemy import (
    select, 
    delete
)
from database import (
    session,
    Base,
    engine,
    Chats
)

def create_table() -> None:
    Base.metadata.create_all(engine)


def update_in_db(chat_name: str, chat_messages: dict) -> None:
    create_table()
    with session as s:
        result = s.scalar(select(Chats).where(Chats.chat_name == chat_name))
        if result:
            result.chat_messages = chat_messages
            s.commit()
        else:
            s.add(
                Chats(
                    chat_name=chat_name,
                    chat_messages=chat_messages
                )
            )
            s.commit()


def delete_in_db(chat_name: str) -> None:
    create_table()
    with session as s:
        s.execute(delete(Chats).where(Chats.chat_name == chat_name))
        s.commit()
        
        
def get_messages_db() -> object:
    create_table()
    with session as s:
        result = s.scalars(select(Chats))
        obs = result.fetchall()
        return obs