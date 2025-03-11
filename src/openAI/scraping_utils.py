import requests
from bs4 import BeautifulSoup
import openai

from config.general import settings

client = openai.OpenAI(api_key=settings.openai_secret_key)


def get_website_content(url: str) -> str:
    """Парсим сайт и собираем полезный текст"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    texts = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        if text:
            texts.append(text)

    return "\n".join(texts)[:5000]


def analyze_with_chatgpt(text: str, question: str) -> str:
    """Отправляет текст сайта (если есть) и вопрос в ChatGPT для анализа"""
    if text:
        prompt = f"Вот текст сайта: {text} \n\nВопрос: {question}"
        system_message = "Твоя задача — проанализировать текст сайта и отвечать на вопросы по нему. И на другие вопрсоы в сообщении"
    else:
        prompt = question
        system_message = "Ты — дружелюбный и полезный, который отвечает на вопросы пользователя."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
