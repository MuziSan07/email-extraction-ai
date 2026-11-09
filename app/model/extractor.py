"""Business-information extraction via an LLM (Groq through LangChain).

The LLM client is created lazily so the application (and its tests) can be
imported without a valid API key present.
"""

import json
from functools import lru_cache

from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

from .. import config
from .schemas import BusinessInfo

_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["email_content"],
    template="""
You are an assistant that MUST extract clean, accurate business contact
information from the FULL EMAIL BODY provided.

Read the entire email body and return ONLY a single valid JSON object with
these exact keys (use empty string "" when data is not present):

- name
- title
- company
- email
- phone
- address
- website
- other_info

Rules:
- Return ONLY the JSON object and nothing else.
- Combine multiple phone numbers with a comma and space.
- Normalize website to include http:// or https:// if missing.
- other_info should include short bullet-like facts separated by " - ".
- Use values only from the email body. Do not invent or fetch external data.

Email Body:
{email_content}

Return ONLY the JSON object.
""",
)


@lru_cache(maxsize=1)
def _get_llm() -> ChatGroq:
    if not config.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a key at https://console.groq.com "
            "and set it in the environment (see .env.example)."
        )
    return ChatGroq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
        temperature=config.GROQ_TEMPERATURE,
    )


def _strip_code_fences(content: str) -> str:
    if "```json" in content:
        return content.split("```json")[1].split("```")[0].strip()
    if "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return content


def extract_business_info(email_content: str) -> BusinessInfo:
    """Extract structured business info from an email body.

    Returns an empty :class:`BusinessInfo` if the model output cannot be
    parsed, so callers always receive a valid object.
    """
    llm = _get_llm()
    prompt = _EXTRACTION_PROMPT.format(email_content=email_content)
    response = llm.invoke(prompt)
    content = _strip_code_fences(response.content.strip())

    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return BusinessInfo()

    # Keep only known fields; ignore anything unexpected the model returns.
    allowed = BusinessInfo.model_fields.keys()
    cleaned = {k: v for k, v in data.items() if k in allowed}
    return BusinessInfo(**cleaned)
