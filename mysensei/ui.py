"""
UI components
"""
from nicegui import app, ui
from typing import Any
from dataclasses import fields, Field
from mysensei.generation import PromptParams, TCConcepts
from mysensei.annotations import PromptParamName


class GenerationUI:
    # TODO: docstr

    def __init__(self, prompt_params: PromptParams)->None:
        self.prompt_params = prompt_params


    def display_whole_ui(self)->None:
        # TODO: docstr
        self._display_fields()

    def _display_fields(self)->None:
        # TODO: docstr
        # Get fields
        prompt_params = self.prompt_params
        param_fields = fields(prompt_params)
        # Loop on fields
        for field in param_fields:
            field_name = field.name
            self._display_field(field_name=field_name)

    def _display_field(self, field_name: PromptParamName)->None:
        # TODO: docstr
        prompt_params = self.prompt_params
        # Inspect field values
        field_value = prompt_params.__getattribute__(field_name)
        # Header
        ui.label(field_name)
        # (Sub)field values
        if isinstance(field_value, str):
            ui.input().bind_value(target_object=prompt_params, target_name=field_name)
        elif isinstance(field_value, dict):
            if all(isinstance(e, str) for e in field_value):
                self._display_subfields(d=field_value)
            elif all(isinstance(e, dict) for e in field_value):
                pass  # TODO
            else:
                raise TypeError() # TODO: write

    def _display_subfields(self, d: dict[str, Any]):
        if all(isinstance(e, str) for e in d.values()):
            self._display_nonnested_subfields(d=d)
        elif all(isinstance(e, dict) for e in d.values()):
            self._display_nested_subfields(d=d)
        else: 
            raise TypeError() # TODO: write

    def _display_nonnested_subfields(self, d: dict[str, str]):
        # TODO: docstr
        for k in d.keys():
            ui.input().bind_value(target_object=d, target_name=k)

    def _display_nested_subfields(self, d: dict[str, dict[str, str]]):
        # TODO: docstr
        for subdict_name, subdict_value in d.items():
            with ui.row():
                self._display_nonnested_subfields(d=subdict_value)

    def display_field_values(self):
        """Display value of fields (for quick checks)"""
        ui.label().bind_text_from(target_object=self, target_name="prompt_params", backward=lambda x: x.__str__())
        


# TO REMOVE
tc_concepts = TCConcepts(target_concept="zzz", component_concepts={"a":"", "b":
""})
tc_concepts = TCConcepts(target_concept="zzz", component_concepts={"m1": {"a": "", "b": ""}, "m2": {"c": "3"}})
generation_ui = GenerationUI(prompt_params=tc_concepts)
generation_ui.display_whole_ui()
generation_ui.display_field_values()
ui.run()
