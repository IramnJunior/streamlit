from langchain_google_genai import ChatGoogleGenerativeAI
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.prompts import (
    ChatPromptTemplate
)

from instructions import instruction

from dotenv import load_dotenv
import os
load_dotenv()

import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0,
    safety_settings=safety_settings
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instruction),
        ("human", "{question}")
    ]
)

chain = prompt | llm

db = SQLDatabase.from_uri(os.environ.get("URL_DATABASE"))

agent_executor = create_sql_agent(
    llm=llm, 
    db=db, 
    agent_type="tool-calling",
    verbose=True,
)