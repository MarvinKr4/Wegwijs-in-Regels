import os

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

VECTOR_DIMS = 3072

llm = AzureChatOpenAI(
    deployment_name=os.getenv("GPT_DEPLOYMENT_NAME"),
    temperature=0,
    api_key=os.getenv("GPT_API_KEY"),
    api_version=os.getenv("GPT_API_VERSION"),
    azure_endpoint=os.getenv("GPT_ENDPOINT"),
)

embeddings = AzureOpenAIEmbeddings(
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
    api_key=os.getenv("EMBEDDINGS_API_KEY"),
    api_version=os.getenv("EMBEDDINGS_API_VERSION"),
    azure_endpoint=os.getenv("EMBEDDINGS_ENDPOINT"),
    dimensions=VECTOR_DIMS,
)


async def invoke(messages) -> str:
    ai_msg = await llm.ainvoke(messages)
    return ai_msg.content


async def get_embedding(query) -> list[float]:
    return await embeddings.aembed_query(query)


async def bulk_embed(docs) -> list[list[float]]:
    return await embeddings.aembed_documents(docs)
