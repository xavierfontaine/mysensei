"""
UI components
"""
from nicegui import app, ui
from typing import Any
from dataclasses import fields, Field
from jinja2 import Template
from mysensei.generation import PromptParams, TCConcepts
from mysensei.annotations import PromptParamName, Prompt
from mysensei.io import get_jinja_template
from mysensei.text import replace_linebreaks_w_br


class GenerationUI:
    """UI for generation

    Display inputable fields, a prompt rendering button, and the prompt itself
    """

    def __init__(self, prompt_params: PromptParams, template_name: str,
                 template_version: str)->None:
        # Init
        self.prompt = ""
        self.can_gen_prompt = False
        # Attach to self
        self.prompt_params = prompt_params
        self.template_name = template_name
        self.template_version = template_version
        # Load template
        self.template = self._load_template()
        # Update initial generability
        self.can_gen_prompt = self._update_can_gen_prompt()

    def display_whole_ui(self)->None:
        """Display the entire UI"""
        self._display_fields()
        self._display_prompt_rendering_button()
        self._display_prompt()

    def _update_can_gen_prompt(self)->bool:
        """Update self.can_gen_prompt depending on whether all prompt
        parameters have been filled out or non"""
        self.can_gen_prompt = (len(self.prompt_params.non_filled_out_fields()) == 0)

    def display_field_values(self)->None:
        """Display value of fields (for quick checks)"""
        ui.label().bind_text_from(target_object=self, target_name="prompt_params", backward=lambda x: x.__str__())

    def _update_prompt(self)->None:
        """Update self.prompt by rendering the template with self.prompt_params"""
        prompt = self.template.render(
            **self.prompt_params.get_filled_out_fields_subfields()
        )
        self.prompt = prompt

    def _load_template(self)->Template:
        """Load the template based on self.template_name and self.template_version"""
        template = get_jinja_template(template_name=self.template_name, version = self.template_version)
        return template

    def _display_fields(self)->None:
        """Display the input fields for prompt parameters"""
        # Get fields
        prompt_params = self.prompt_params
        param_fields = fields(prompt_params)
        # Loop on fields
        for field in param_fields:
            field_name = field.name
            self._display_field(field_name=field_name)

    def _display_field(self, field_name: PromptParamName)->None:
        """Display one field"""
        prompt_params = self.prompt_params
        # Inspect field values
        field_value = prompt_params.__getattribute__(field_name)
        # Header
        ui.label(field_name)
        # (Sub)field values
        if isinstance(field_value, str):
            ui.input(on_change=self._update_can_gen_prompt).bind_value(target_object=prompt_params, target_name=field_name)
        elif isinstance(field_value, dict):
            self._display_subfields(d=field_value)

    def _display_subfields(self, d: dict[str, Any])->None:
        """Display the subfields of field if field is dictionary of subfields"""
        if all(isinstance(e, str) for e in d.values()):
            self._display_nonnested_subfields(d=d)
        elif all(isinstance(e, dict) for e in d.values()):
            self._display_nested_subfields(d=d)
        else: 
            raise TypeError()

    def _display_nonnested_subfields(self, d: dict[str, str])->None:
        """Display when field is dict of str fields"""
        for k in d.keys():
            ui.input(on_change=self._update_can_gen_prompt).bind_value(target_object=d, target_name=k)

    def _display_nested_subfields(self, d: dict[str, dict[str, str]])->None:
        """Display when field is dict of subfields"""
        for subdict_name, subdict_value in d.items():
            with ui.row():
                self._display_nonnested_subfields(d=subdict_value)

    def _display_prompt(self)->None:
        """Display prompt"""
        ui.markdown().bind_content_from(
            target_object=self,
            target_name="prompt",
            backward=replace_linebreaks_w_br
        ).bind_visibility_from(target_object=self, target_name="can_gen_prompt")

    def _display_prompt_rendering_button(self)->None:
        """Display prompt rendering button"""
        ui.button(
            text="Get prompt", 
            on_click=self._update_prompt
        ).bind_enabled_from(target_object=self, target_name="can_gen_prompt")
        


# TO REMOVE
tc_concepts = TCConcepts(target_concept="zzz", component_concepts={"a":"", "b":
""})
tc_concepts = TCConcepts(target_concept="zzz", component_concepts={"m1": {"a": "", "b": ""}, "m2": {"c": "3"}})
generation_ui = GenerationUI(prompt_params=tc_concepts,
                             template_name="pure_concepts",
                             template_version=0)
generation_ui.display_whole_ui()
generation_ui.display_field_values()
ui.run()
