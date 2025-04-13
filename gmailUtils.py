from langchain_google_community import GmailToolkit
import openai


toolkit = GmailToolkit(force_refresh=True)


mailTools = toolkit.get_tools()
