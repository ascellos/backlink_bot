import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("DEBUG - Loaded key:", repr(os.getenv("GROQ_API_KEY")))

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def generate_article(client_site: str, target_site: str, niche: str, anchor_text: str = None, company_name: str = None, seed_keyword: str = None):
    if anchor_text:
        anchor_instruction = f'The clickable link text (anchor text) MUST be exactly: "{anchor_text}"'
    else:
        anchor_instruction = ""

    if seed_keyword and not anchor_text:
        keyword_link_instruction = f'CRITICAL: Somewhere in the middle of the article body (not at the end, not on its own line), write a short natural sentence (5-10 words) that includes a bolded, hyperlinked phrase like this exact format: **<a href="{client_site}">3-6 word phrase with {seed_keyword}</a>**. Example: "Businesses can improve results with **<a href="{client_site}">expert {seed_keyword} solutions</a>**."'
    else:
        keyword_link_instruction = ""

    if seed_keyword and not anchor_text:
        link_requirement = f'IMPORTANT: The article MUST include exactly ONE clickable HTML hyperlink to {client_site} — this is the same link described in the CRITICAL instruction below. Do not add any other links to {client_site}.'
    else:
        link_requirement = f'''IMPORTANT: The article MUST include exactly one clickable HTML hyperlink to {client_site}, 
    formatted like this: <a href="{client_site}">anchor text</a>
    Do NOT just mention the brand name in plain text — it must be an actual HTML link.'''

    if seed_keyword:
        keyword_instruction = f'The article title/heading MUST prominently feature the keyword "{seed_keyword}" (expand it naturally into a compelling long-tail phrase if needed).'
    else:
        keyword_instruction = "Choose a relevant topic heading for the article naturally."

    if company_name:
        company_instruction = f'Mention the company name "{company_name}" in **bold** at least once in the article.'
    else:
        company_instruction = ""

    prompt = f"""
    Write a 600-word blog article suitable for guest posting on a site in the "{niche}" niche.

    {link_requirement}
    {anchor_instruction}
    {keyword_link_instruction}
    {keyword_instruction}
    {company_instruction}

    Make it informative, well-structured with a title, intro, 2-3 subheadings, and a conclusion.
    The tone should be professional and engaging, written for a blog audience.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    result = generate_article(
        client_site="https://www.foxydigits.com",
        target_site="https://example.com",
        niche="digital marketing",
        company_name="Foxy Digits",
        seed_keyword="marketing"
    )
    print(result)