"""
UI components
"""
from nicegui import app, ui
from typing import Any, Optional
from dataclasses import fields, Field
from jinja2 import Template
from mysensei.generation import PromptParams, TCParams, TCRevisionParams
from mysensei.annotations import PromptParamName, Prompt
from mysensei.io import get_jinja_template
from mysensei.text import replace_linebreaks_w_br


class PromptUI:
    #TODO: docstr (init parameters)
    """UI for generation

    Display inputable fields, a prompt rendering button, and the prompt itself
    """

    def __init__(self, prompt_params: PromptParams, template_name: str,
                 template_version: str,
                 hidden_fields:Optional[list[PromptParamName]]=None,
                 multirow_fields:Optional[list[PromptParamName]]=None,
                )->None:
        # Init
        self.prompt = ""
        self.can_gen_prompt = False
        # Attach to self
        self.prompt_params = prompt_params
        self.template_name = template_name
        self.template_version = template_version
        self.hidden_fields = []
        if hidden_fields is None:
            self.hidden_fields = []
        else:
            self._update_hidden_fields(fields_to_hide=hidden_fields)
        if multirow_fields is None:
            self.multirow_fields = []
        else:
            self._update_multirow_fields(fields_to_expand=multirow_fields)
        # Load template
        self.template = self._load_template()
        # Update initial generability
        self.can_gen_prompt = self._update_can_gen_prompt()

    def display_whole_ui(self)->None:
        """Display the entire UI"""
        self._display_fields()
        self._display_prompt_rendering_button()
        self._display_prompt()

    def _update_hidden_fields(self, fields_to_hide: list[PromptParamName]):
        for f in fields_to_hide:
            if f not in self.prompt_params._get_fields_names():
                raise KeyError(
                    f"Field {f} in `hidden_fields`, but not one of the"
                    f" parameters {self.prompt_params._get_fields_names()}"

                )
        self.hidden_fields = fields_to_hide

    def _update_multirow_fields(self, fields_to_expand: list[PromptParamName]):
        for f in fields_to_expand:
            if f not in self.prompt_params._get_fields_names():
                raise KeyError(
                    f"Field {f} in `multirow_fields`, but not one of the"
                    f" parameters {self.prompt_params._get_fields_names()}"

                )
        self.multirow_fields = fields_to_expand

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
            if field_name not in self.hidden_fields:
                self._display_field_orchestrator(field_name=field_name)

    def _display_field_orchestrator(self, field_name: PromptParamName)->None:
        """Display one field, with label and subfields if any"""
        prompt_params = self.prompt_params
        # Inspect field values
        field_value = prompt_params.__getattribute__(field_name)
        # Header
        ui.label(field_name)
        # (Sub)field values
        if isinstance(field_value, str):
            self._field_inputer(field_name=field_name,
                                binding_target_object=prompt_params,
                                binding_target_name=field_name)
        elif isinstance(field_value, dict):
            self._display_subfields(d=field_value, field_name=field_name)

    def _field_inputer(
        self, 
        field_name: PromptParamName, 
        binding_target_object: Any,
        binding_target_name: str
    ):
        """Display inputation area"""
        if field_name in self.multirow_fields:
            ui.textarea(on_change=self._update_can_gen_prompt).bind_value(target_object=binding_target_object,
                                                                          target_name=binding_target_name)
        else:
            ui.input(on_change=self._update_can_gen_prompt).bind_value(target_object=binding_target_object,
                                                                       target_name=binding_target_name)


    def _display_subfields(self, field_name: PromptParamName, d: dict[str, Any])->None:
        """Display the subfields of field if field is dictionary of subfields"""
        if all(isinstance(e, str) for e in d.values()):
            self._display_nonnested_subfields(field_name=field_name, d=d)
        elif all(isinstance(e, dict) for e in d.values()):
            self._display_nested_subfields(field_name=field_name, d=d)
        else: 
            raise TypeError()

    def _display_nonnested_subfields(self, field_name: PromptParamName, d: dict[str, str])->None:
        """Display when field is dict of str fields"""
        for k in d.keys():
            self._field_inputer(field_name=field_name,
                                binding_target_object=d,
                                binding_target_name=k)

    def _display_nested_subfields(self, field_name: PromptParamName, d: dict[str, dict[str, str]])->None:
        """Display when field is dict of subfields"""
        for subdict_name, subdict_value in d.items():
            with ui.row():
                self._display_nonnested_subfields(field_name=field_name, d=subdict_value)


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
