# 提示词

## Python - 生成PDF Reader

按照以下要求生成一个Python函数。

函数名
- LoadPdfIntoChromDB

参数
- PDF文件的目录
- chunk size
- chunk overlap
- separator
- embed_model_name
- embedding model API base URL
- ChromaDB persist dir
- ChromaDB collection name
- whether to clear chromaDB flag

返回值
- 处理过程中的Log，比如处理了多少个PDF，中间有没有什么错误。

实现
- embedding model可以直接调用我已经写好的get_embeddings(embed_model_name, base_url)函数来获取embedding_function