import os
import re
import glob
import time
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader, PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Global constants
MARKDOWN_DIR = r"\\mazda\AI\materials\DAQmx\hardware\mds"
PDF_DIR = "../../../docs/pdfs"
PERSIST_DIR = 'c:\chroma_db'
COLLECTION_NAME = 'daqmx-test'

TEMPERATURE = 0.2

# EMBED_BASE_URL = 'mazda:11433'
# EMBED_MODEL_NAME = 'rjmalagon/gte-Qwen2-7B-instruct:f16'
# EMBED_MODEL_NAME = 'mxbai-embed-large'
# USE_OLLAMA = True
EMBED_BASE_URL = 'http://sh-rd-rgao3:1234/v1'
EMBED_MODEL_NAME = 'mixedbread-ai/mxbai-embed-large-v1'
USE_OLLAMA = False

BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = "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"
MODEL_NAME = "qwen/qwq-32b"

# BASE_URL = "http://10.144.128.8:1234/v1"
# API_KEY = "not-needed"
# MODEL_NAME = "deepseek-r1-distill-qwen-1.5b"

#query = "What is the maximum voltage range of NI 9225? What's the price?"
# query = "NI 9225的最高电压是多少？它的售价是多少？"
#query = "NI 9437能用来测试什么信号？"
#query = "How many analog inputs does NI 9230 have?"
query = "NI 9230有多少个模拟输入？"
#query = "如何使用NI DAQmx测量角位移？"

ASSISTANT_SYSTEM_PROMPT="Note that when users ask questions about NI hardware, cDAQ-xxxx, NI-xxxx and \"NI xxxx\" refer to the same hardware. \
    e.g. cDAQ-9219 is the same hardware as NI-9219 or \"NI 9219\"."

def LoadPdfIntoChromDB(
    pdf_directory,
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n"],
    embed_model_name="text-embedding-ada-002",
    embedding_api_base_url=None,
    chroma_persist_dir="./chromadb",
    chroma_collection_name="pdf_collection",
    clear_chromadb=False
):
    """
    Loads PDF files from a directory into ChromaDB using LangChain.
    Args:
        pdf_directory (str): Directory containing PDF files
        chunk_size (int): Size of text chunks for splitting
        chunk_overlap (int): Overlap between chunks
        separator (str): Separator for text splitting
        embed_model_name (str): Name of the embedding model
        embedding_api_base_url (str): Base URL for embedding model API
        chroma_persist_dir (str): Directory to persist ChromaDB
        chroma_collection_name (str): Name of the ChromaDB collection
        clear_chromadb (bool): Whether to clear existing ChromaDB data
        
    Returns:
        str: Log of the processing
    """

    log = []
    start_time = time.time()

    # Log start of process
    log.append(f"Starting to load PDFs from {pdf_directory}")

    try:
        # Check if PDF directory exists
        if not os.path.exists(pdf_directory):
            raise FileNotFoundError(f"PDF directory does not exist: {pdf_directory}")
        
        # Count PDF files in directory
        pdf_files = glob.glob(os.path.join(pdf_directory, "**/*.pdf"), recursive=True)
        log.append(f"Found {len(pdf_files)} PDF files in {pdf_directory}")
        
        if not pdf_files:
            log.append("No PDF files found. Exiting.")
            return True, "\n".join(log)
        
        # Load PDFs from directory
        loader = DirectoryLoader(pdf_directory, glob="**/*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        pdf_count = len(set([doc.metadata.get('source', '') for doc in documents]))
        log.append(f"Loaded {len(documents)} pages from {pdf_count} PDF files")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators
        )
        splits = text_splitter.split_documents(documents)
        log.append(f"Split into {len(splits)} chunks")
        
        # Get embedding function using the provided function
        embedding_function = get_embeddings(
            embed_model_name,
            embedding_api_base_url,
            isOllama=False
        )
        
        # Initialize ChromaDB
        if clear_chromadb and os.path.exists(chroma_persist_dir):
            import shutil
            shutil.rmtree(chroma_persist_dir)
            log.append(f"Cleared existing ChromaDB at {chroma_persist_dir}")
        
        # Create vector store
        log.append(f"Creating vector store in {chroma_persist_dir} with collection name {chroma_collection_name}")
        vectordb = Chroma.from_documents(
            documents=splits,
            embedding=embedding_function,
            persist_directory=chroma_persist_dir,
            collection_name=chroma_collection_name
        )
        log.append(f"Successfully stored {len(splits)} chunks in ChromaDB collection '{chroma_collection_name}'")
        
        elapsed_time = time.time() - start_time
        log.append(f"Total processing time: {elapsed_time:.2f} seconds")
    
    except Exception as e:
        log.append(f"Error: {str(e)}")
        import traceback
        log.append(f"Traceback: {traceback.format_exc()}")
        return True, "\n".join(log)

    return False, "\n".join(log)

def get_embeddings(embed_model_name, base_url, isOllama):
    # Embedding using Ollama embeddings model
    if isOllama:
        return OllamaEmbeddings(model=embed_model_name, base_url=base_url)
    else:
        return OpenAIEmbeddings(
            model=embed_model_name,
            openai_api_base=base_url,
            openai_api_key="not-needed",
            check_embedding_ctx_length=False,
        )

def ProcessMarkdownFiles(
    markdown_dir, 
    chunk_size, 
    chunk_overlap, 
    separators, 
    embed_model_name, 
    base_url, 
    persist_dir, 
    collection_name, 
    clear=True, 
    isOllama=False
):
    # 加载Markdown文件
    loader = DirectoryLoader(markdown_dir, loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()

    for doc in documents:
        # parse the file name without extension from the full path "doc.metadata["source"]"
        file_name = os.path.splitext(os.path.basename(doc.metadata["source"]))[0]
        doc.metadata["model"] = doc.metadata["source"]
        print(file_name)

    # 递归拆分成chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size,
        chunk_overlap,
        separators
    )
    texts = text_splitter.split_documents(documents)

    embeddings = get_embeddings(embed_model_name, base_url, isOllama)

    # Delete the existing collection
    if clear:
        db = Chroma(collection_name=collection_name, persist_directory=persist_dir)
        db.delete_collection()

    # 存入向量数据库
    Chroma.from_documents(
        texts, 
        embeddings, 
        persist_directory=persist_dir, 
        collection_name=collection_name
    )

    return

def RetrieveContextsByUserQuery(collection_name, persist_directory, query, model_url, embedding_model_name, k=5, isOllama=False):
    embeddings = get_embeddings(embedding_model_name, model_url, isOllama)
    db = Chroma(collection_name=collection_name, persist_directory=persist_directory, embedding_function=embeddings)

    # 检索
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})

    # Query contexts from db by user query
    results = retriever.invoke(query)
    rag_context = "\n".join([doc.page_content for doc in results])

    return rag_context

def AskLLM(user_query, model_name, temperature, api_key, base_url, system_prompt="", rag_context=""):
    # Construct a combined prompt with rag context and user query when rag_context is not empty.
    # Remove leading/trailing whitespace
    trimmed_context = rag_context.strip()  
    if trimmed_context:
        combined_prompt = f"Context: {trimmed_context}\n\nUser Query: {user_query}"
    else:
        combined_prompt = user_query

    # Create a LLM model using ChatOpenAI with no API-KEY and local URL.
    model = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url
    )
    
    # Send the system_prompt and combined prompt to LLM if system_prompt is not empty.
    trimmed_system_prompt = system_prompt.strip()
    if trimmed_system_prompt:
        response = model.invoke([
            {'role': 'system', 'content': trimmed_system_prompt},        
            {'role': 'user', 'content': combined_prompt}
        ])
    else:
        response = model.invoke([
            {'role': 'user', 'content': combined_prompt}
        ])

    response_content = response.content
    final_answer = re.sub(r'.*?</think>', '', response_content, flags=re.DOTALL).strip()
    return final_answer

if __name__ == "__main__":
    #doc = json_to_documents(r"\\mazda\AI\materials\DAQmx\api_json\mxcreatechannel.json")
    # print(doc)
    # db = ProcessMarkdownFiles(
    #     markdown_dir=MARKDOWN_DIR,
    #     chunk_size=500,
    #     chunk_overlap=50,
    #     separators=["\n## ", "\n### ", "\n#### ", "\n", " ", ""],
    #     embed_model_name=EMBED_MODEL_NAME,
    #     base_url=EMBED_BASE_URL,
    #     persist_dir=PERSIST_DIR,
    #     collection_name=COLLECTION_NAME,
    #     clear=True,
    #     isOllama=USE_OLLAMA
    # )

    hasError, log = LoadPdfIntoChromDB(
        pdf_directory=PDF_DIR,
        chunk_size=10000,
        chunk_overlap=1000,
        separators="\n",
        embed_model_name=EMBED_MODEL_NAME,
        embedding_api_base_url=EMBED_BASE_URL,
        chroma_persist_dir=PERSIST_DIR,
        chroma_collection_name=COLLECTION_NAME,
        clear_chromadb=True
    )

    print("LoadPdf log", log)
    if hasError:
        exit(1)

    rag_context = RetrieveContextsByUserQuery(
        collection_name=COLLECTION_NAME, 
        persist_directory=PERSIST_DIR,
        query=query,
        model_url=EMBED_BASE_URL,
        embedding_model_name=EMBED_MODEL_NAME,
        k=10,
        isOllama=USE_OLLAMA
    )

    print("rag_context: \n", rag_context)    
    print("\nrag_context: end\n")

    # Send the context and user query to LLM
    final_answer = AskLLM(
        user_query=query,
        model_name=MODEL_NAME,
        temperature=TEMPERATURE,
        api_key=API_KEY,
        base_url=BASE_URL,
        rag_context=rag_context,
        system_prompt=ASSISTANT_SYSTEM_PROMPT
    )
    print("answer: \n", final_answer)
    print("\nanswer: end\n")
