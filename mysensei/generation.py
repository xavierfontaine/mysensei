"""
Tools for text generation
"""
import openai
from dataclasses import dataclass, fields
from typing import Any, Union
from jinja2 import Template

import mysensei.io as ms_io
from mysensei.annotations import TargetConcept, ComponentConcept, PromptParamName


# =========
# Constants
# =========
_API_KEY = ms_io.get_conf_toml("secrets.toml")["open_ai"]["api_key"]


# =================
# Prompt parameters
# =================
class PromptFieldTypeError(Exception):
    """A prompt field has an unexpected type"""
    pass


@dataclass
class PromptParams:
    """A generic dataclass for fromp parameters. 

    Fields must be str, dict[str, str] or dict[str, dict[str, str]]
    """
    pass

    def non_filled_out_fields(self)->list[PromptParamName]:
        """Return non-optional fields that haven't been filled out.

        For dict fields, we need at least one element to be non-null."""
        non_field_out = []
        self_fields = fields(self)
        for field in self_fields:
            field_name = field.name
            field_value = self.__getattribute__(field_name)
            if not self._field_is_filled_out(field_value=field_value,
                                              field_name=field_name):
                non_field_out.append(field_name)
        return non_field_out

    def _field_is_filled_out(self, field_value: str, field_name: str)->bool:
        """Check if all fields are str or nested dict of str with at least one
        non-null value"""
        if isinstance(field_value, str):
            return field_value != ""
        elif isinstance(field_value, dict):
            return self._is_nested_dict_nonempty_str(d=field_value,
                                            field_name=field_value)
        else:
            raise PromptFieldTypeError(self._field_error_message(field_name=field_name))
    
    def _is_nested_dict_nonempty_str(self, d:dict, field_name: str)->bool:
        """Is field a (nested or plain) dict of str, with some non-empty?"""
        if len(d) == 0:
            return False
        elif all(isinstance(v, str) for v in d.values()):
            if all(v == "" for v in d.values()):
                return False
        elif all(isinstance(v, dict) for v in d.values()):
            for v in d.values():
                self._is_nested_dict_nonempty_str(d=v, field_name=field_name)
        else:
            raise PromptFieldTypeError(self._field_error_message(field_name=field_name))
        return True

    @staticmethod
    def _field_error_message(field_name: str)->str:
        """Return error msg for field type errors"""
        error_msg = "Field {field_name} is not str, dict[str, str] or dict[str, dict[str, str]]"
        return error_msg.format(field_name=field_name)


@dataclass
class TCConcepts(PromptParams):
    """
    Associate a Target concept (to learn,) with Component concepts (available
    at the time of recall.)
    """
    target_concept: TargetConcept
    component_concepts: dict[str, ComponentConcept]


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
