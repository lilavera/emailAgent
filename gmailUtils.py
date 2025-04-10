from langchain_google_community import GmailToolkit
import openai


toolkit = GmailToolkit()


tools = toolkit.get_tools()

