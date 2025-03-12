import openai

from config.general import settings

client = openai.OpenAI(api_key=settings.openai_secret_key)


def analyze_with_chatgpt(text: str, question: str) -> str:
    """Отправляет текст сайта (если есть) и вопрос в ChatGPT для анализа"""
    if text:
        prompt = f"Вот текст сайта: {text} \n\nВопрос: {question}"
        system_message = "Твоя задача — проанализировать текст сайта и отвечать на вопросы по немуна том языке на котором он спрашивает. И на другие вопрсоы в сообщении"
    else:
        prompt = question
        system_message = "Ты — дружелюбный и полезный, и отвечаешь на вопросы пользователя на том языке на котором он спрашивает."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
