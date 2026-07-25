import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("DEBUG - Loaded key:", repr(os.getenv("GROQ_API_KEY")))

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def generate_article(client_site: str, target_site: str, niche: str, anchor_text: str = None):
    if anchor_text:
        anchor_instruction = f'The clickable link text (anchor text) MUST be exactly: "{anchor_text}"'
    else:
        anchor_instruction = "Choose a natural, descriptive phrase related to the article content as the anchor text."

    prompt = f"""
    Write a 600-word blog article suitable for guest posting on a site in the "{niche}" niche.

    IMPORTANT: The article MUST include exactly one clickable HTML hyperlink to {client_site}, 
    formatted like this: <a href="{client_site}">anchor text</a>
    Do NOT just mention the brand name in plain text — it must be an actual HTML link.
    {anchor_instruction}

    Make it informative, well-structured with a title, intro, 2-3 subheadings, and a conclusion.
    The tone should be professional and engaging, written for a blog audience.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content