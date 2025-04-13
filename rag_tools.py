from langchain.tools import Tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


loader = TextLoader("faq.txt")
docs = loader.load()


splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap=60)
chunks = splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
vectorestore = FAISS.from_documents(chunks,embeddings)

retriever = vectorestore.as_retriever()

rag_tool = Tool(
    name="KnowledgeBaseSearch",
    description="Use this tool to answer technical questions about AI agents using internal documentation.",
    func=lambda query: "\n".join(
        [doc.page_content for doc in retriever.get_relevant_documents(query)])
)
