import openai
from dotenv import load_dotenv
import os
from gmailUtils import mailTools
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import chat_agent_executor
from prompts import *
from langchain.prompts import PromptTemplate
import re


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

mailTools = [*mailTools]

model = ChatOpenAI(model="gpt-4o")


def agent_executor(prompt):
    response = chat_agent_executor.create_tool_calling_executor(model, mailTools).invoke(
        {"messages": [HumanMessage(content=prompt)]})
    # print(response)
    ai_response = [msg.content for msg in response["messages"]
                   if isinstance(msg, AIMessage)]
    print(ai_response)
    return ai_response


def get_and_categorize_email():
    # categorize_prompt = PromptTemplate(template=GET_AND_CATEGORIZE_EMAIL_PROMPT).format()
    result = agent_executor(GET_AND_CATEGORIZE_EMAIL_PROMPT)
    return result


# Example usage:
categorize = agent_executor(PromptTemplate(
    template=GET_AND_CATEGORIZE_EMAIL_PROMPT).format())
defined_email_category = re.findall(r"\*\*(.*?)\*\*", categorize[1])


formatted_prompt = CREATE_DRAFT_PROMPT.format(category=defined_email_category)

create_draft_message = agent_executor(formatted_prompt)
send_message = agent_executor(PromptTemplate(
    template=SEND_THE_EMAIL_PROMPT).format())
