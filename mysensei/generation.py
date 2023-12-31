"""
Tools for text generation
"""
import openai
from copy import deepcopy
from dataclasses import dataclass, fields, Field
from typing import Any, Union, Literal
from jinja2 import Template

import mysensei.io as ms_io
from mysensei.annotations import TargetConcept, ComponentConcept, PromptParamName, Prompt


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

    Fields must be str, dict[str, str] or dict[str, dict[str, str]].
    """
    pass

    def non_filled_out_fields(self)->list[PromptParamName]:
        """Return non-optional fields that haven't been filled out.

        For dict fields, we need at least one element to be non-null."""
        non_field_out = []
        fields_names = self._get_fields_names()
        for field_name in fields_names:
            field_value = self._get_field_attribute(field_name=field_name)
            if not self._field_is_filled_out(field_value=field_value,
                                              field_name=field_name):
                non_field_out.append(field_name)
        return non_field_out

    def get_filled_out_fields_subfields(self)->dict[PromptParamName, 
        Union[str, dict[str, str], dict[str, dict[str, str]]]]:
        """Return the dict of parameters, leaving out empty fields/subfields"""
        # Drop the empty fields
        filled_field_names = [n for n in self._get_fields_names() if n not in
            self.non_filled_out_fields()]
        output = {
            n: deepcopy(self._get_field_attribute(field_name=n)) 
            for n in filled_field_names
        }
        # Drop the empty subfields
        for field_name, field_value in output.items():
            if isinstance(field_value, dict):
                subfields_to_drop = []
                for subfield_name, subfield_value in field_value.items():
                    if not self._field_is_filled_out(field_value=subfield_value, field_name=subfield_name):
                        subfields_to_drop.append(subfield_name)
                [field_value.pop(to_drop) for to_drop in subfields_to_drop]
        return output

    def _get_fields_names(self)->list[PromptParamName]:
        """Return all fields (class attributes)"""
        return [f.name for f in fields(self)]

    def _get_field_attribute(self, field_name: str)->Union[str, dict[str, str], dict[str, dict[str, str]]]:
        """Return value associated to a field"""
        return self.__getattribute__(field_name)

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
class TCParams(PromptParams):
    """
    Associate a Target concept (to learn,) with Component concepts (available
    at the time of recall.)
    """
    target_concept: TargetConcept
    component_concepts: dict[str, ComponentConcept]


@dataclass
class TCRevisionParams(PromptParams):
    """
    Inherits from TCParams. Used for mnemonic revision.
    """
    mnemonic: str


@dataclass
class TCSoundParams(PromptParams):
    """
    Associate a Target concept (to learn,) with the *sound* of a Component concepts.
    """
    target_concept: TargetConcept
    component_concepts_sounds: dict[str, dict[Literal["concept", "details", "sound"], str]]
    meaning_mnemonic: str


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
