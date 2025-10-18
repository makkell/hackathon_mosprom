from dotenv import load_dotenv
from .prompt import PROMPT
from gigachat import GigaChat
import os

load_dotenv()

API_KEY_GIGACHAT = os.getenv("GIGACHAT_API_KEY")

def get_llm_answer(metrics_text):
    """
    Получает рекомендации от LLM на основе метрик
    
    Args:
        metrics_text (str): Форматированный текст с метриками
        
    Returns:
        str: Рекомендации от LLM
    """

        # Инициализируем GigaChat с правильными параметрами
    giga = GigaChat(
        credentials=API_KEY_GIGACHAT,
        model='GigaChat-2',
        verify_ssl_certs=False,
        scope='GIGACHAT_API_PERS'
    )

    # Формируем промпт с метриками
    payload = PROMPT.format(metrics=metrics_text)

    # Отправляем запрос
    resp = giga.chat(payload)

    return resp.choices[0].message.content

   