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
openai.api_key = _API_KEY


# TODO: clean
print([m["id"] for m in openai.Model.list()["data"] if "4" in m["id"]])
# TODO: clean
