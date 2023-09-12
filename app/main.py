"""
Interface for creating prompts
"""
from nicegui import app, ui

from mysensei.generation import PromptParams, TCParams, TCRevisionParams, TCSoundParams
from mysensei.ui import PromptUI


# ==========
# Parameters
# ==========
N_CONCEPTS = 4


# ==========
# Components
# ==========
def display_target_component_ui():
    tc_concepts = TCParams(target_concept="", 
                           component_concepts={"concept"+str(i): "" for i in range(N_CONCEPTS)})
    #TODO: tc_concepts cannot be passed by reference. Repair. Add mapping
    # system from one PromptParams to the other. To do that, need to add a
    # method that creates/update such fields, with reference to the other
    # PromptParams and the associated fields.
    mnem_revision = TCRevisionParams(mnemonic = "")
    mnem_prompt_ui = PromptUI(prompt_params=tc_concepts,
                                 template_name="pure_concepts",
                                 template_version=0)
    mnem_revision_ui = PromptUI(prompt_params=mnem_revision,
                                auxiliary_prompt_params_lst=[tc_concepts],
                                 template_name="pure_concepts_revision",
                                 template_version=0,
                                 multirow_fields=["mnemonic"])
    with ui.row().classes("w-full"):
        with ui.card().classes("w-2/5"):
            mnem_prompt_ui.display_whole_ui()
        with ui.card().classes("w-2/5"):
            mnem_revision_ui.display_whole_ui()
            mnem_revision_ui.display_field_values()

def display_kanji_ui():
    tc_sound_concepts = TCSoundParams(target_concept="zzz", component_concepts={"a":"", "b": ""})
    pass

display_target_component_ui()
ui.run()
