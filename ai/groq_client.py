from groq import Groq
import config

_client = None


def get_client():
    """Returns a cached Groq client instance. Raises a clear error if the API key is missing."""
    global _client
    if not config.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to your .env file (local) "
            "or Streamlit Secrets (deployment)."
        )
    if _client is None:
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client