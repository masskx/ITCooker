from langchain_openai import ChatOpenAI
from config.llm_config import lm_config

_llm_client_cache = {}

def get_llm_client(model:str|None=None,json_model:bool=False):
    m = model or lm_config.llm_model
    key = (m, json_model)

    if key in _llm_client_cache: # 如果模型有，就直接返回
        return _llm_client_cache[key] # 模型名字对应模型对象
    model_kwargs = {}

    if json_model:
        model_kwargs["response_format"] = {"type":"json_object"}

    client = ChatOpenAI(
        model=m,
        temperature=lm_config.llm_temperature,
        base_url=lm_config.base_url,
        api_key=lm_config.api_key,
        model_kwargs=model_kwargs
    )
    _llm_client_cache[key] = client

    return client
if __name__ == '__main__':

    client = get_llm_client()
    res = client.invoke("nihao!")
    print(res)