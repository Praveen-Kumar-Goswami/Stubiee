# llama_client.py
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(
    base_url="https://chatapi.akash.network/api/v1",
    api_key="sk-5F7Kna9Tb3gxGsXWYo0KlA",  # Replace with your actual API key
)

def get_llama_response(user_input: str, image_url: str = "") -> str:
    # Prepare message content
    content = [{"type": "text", "text": user_input}]
    if image_url.strip():
        content.append({"type": "image_url", "image_url": {"url": image_url.strip()}})

    try:
        completion = client.chat.completions.create(
            model="Meta-Llama-3-1-8B-Instruct-FP8",
            messages=[{"role": "user", "content": content}],
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
                "X-Title": "<YOUR_SITE_NAME>",  # Optional
            },
            extra_body={},
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
