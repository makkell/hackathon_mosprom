from pyexpat import model
from dotenv import load_dotenv
from prompt import PROMPT
from gigachat import GigaChat
import os

load_dotenv()

context_messages = '' # данные которые будут использоваться для контекста (все метрики и прочее)

API_KEY_GIGACHAT = os.getenv("API_KEY_GIGACHAT")

def get_llm_answer(prompt):
    giga = GigaChat(
    crecredentials=API_KEY_GIGACHAT,
    model='GigaChat-2', # Лучше заменить на Max 
    verify_ssl_certs=False,
    )

    payload = PROMPT.format(metrics=context_messages)

    resp = giga.chat(payload)

    return resp.choices[0].message.content