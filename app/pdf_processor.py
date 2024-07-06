import os
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.readers.file import PDFReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

def get_index(data, index_name):
    if not os.path.exists(index_name):
        print(f"Building index {index_name}")
        index = VectorStoreIndex.from_documents(data, show_progress=True)
        index.storage_context.persist(persist_dir=index_name)
    else:
        print(f"Loading existing index {index_name}")
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_name)
        )
    return index

def process_pdf(pdf_path):
    pdf_data = PDFReader().load_data(file=pdf_path)
    index_name = f"index_{os.path.basename(pdf_path).replace('.pdf', '')}"
    get_index(pdf_data, index_name)
    return index_name

def get_query_engine(index_name):
    index = load_index_from_storage(
        StorageContext.from_defaults(persist_dir=index_name)
    )
    return index.as_query_engine()

def query_pdf(index_name, query):
    query_engine = get_query_engine(index_name)
    llm = OpenAI(model="gpt-3.5-turbo")
    tool = QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="pdf_tool",
            description="This tool provides information from the processed PDF"
        )
    )
    agent = ReActAgent.from_tools([tool], llm=llm, verbose=True)
    result = agent.query(query)
    return str(result)
