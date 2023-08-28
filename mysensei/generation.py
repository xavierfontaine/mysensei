"""
Tools for text generation
"""
import openai

import mysensei.io as ms_io


# =========
# Constants
# =========
_API_KEY = ms_io.get_conf_toml("secrets.toml")["open_ai"]["api_key"]


# ======
# OpenAI
# ======
# Set up API key
openai.api_key = _API_KEY


def generate_gpt4_simple(prompt: str)->str:
    """
    Straightforward prompt -> output generation with gpt4
    """
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt},]
    )
    output = completion.choices[0].message.content
    return output
