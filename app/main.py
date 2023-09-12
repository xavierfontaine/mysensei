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
def _displayer(sub_prompt_uis: list[PromptUI]):
    """Display prompt uis uniformly"""
    if len(sub_prompt_uis) == 1:
        with ui.card().classes("w-full"):
            sub_prompt_uis[0].display_whole_ui()
    elif len(sub_prompt_uis) == 2:
        with ui.row().classes("w-full"):
            with ui.card().classes("w-2/5"):
                sub_prompt_uis[0].display_whole_ui()
            with ui.card().classes("w-2/5"):
                sub_prompt_uis[1].display_whole_ui()
                sub_prompt_uis[1].display_field_values()
    else:
        raise NotImplemented("Display for more than 2 sub-uis is not implemented")

def display_target_component_ui():
    # Init prompt parameters
    tc_concepts = TCParams(target_concept="", 
                           component_concepts={"concept"+str(i): "" for i in range(N_CONCEPTS)})
    mnem_revision = TCRevisionParams(mnemonic = "")
    # Unit UI classes
    mnem_prompt_ui = PromptUI(prompt_params=tc_concepts,
                                 template_name="pure_concepts",
                                 template_version=0)
    mnem_revision_ui = PromptUI(prompt_params=mnem_revision,
                                auxiliary_prompt_params_lst=[tc_concepts],
                                 template_name="pure_concepts_revision",
                                 template_version=0,
                                 multirow_fields=["mnemonic"])
    # Display UI
    _displayer(sub_prompt_uis=[mnem_prompt_ui, mnem_revision_ui])


def display_reading_ui():
    # Init prompt parameters
    tc_sound_concepts = TCSoundParams(
        target_concept="",
        component_concepts_sounds={
            str(i): {"concept": "", "details": "", "sound": ""}
            for i in range(N_CONCEPTS)
        },

    meaning_mnemonic="")
    # Unit UI classes
    reading_ui = PromptUI(prompt_params=tc_sound_concepts,
                                 template_name="reading_mnem",
                                 template_version=0,
                                 multirow_fields=["meaning_mnemonic"])
    # Display UI
    _displayer(sub_prompt_uis=[reading_ui])


# ==========
# Overall UI
# ==========
# List ui functions
SUB_UI_FUNS = {"meaning": display_target_component_ui, "reading": display_reading_ui}
DEFAULT_TAB = "meaning"

def display_ui():
    tab_dict = {}
    with ui.tabs().classes('w-full') as tabs:
        for tab_name in SUB_UI_FUNS.keys():
            tab_dict[tab_name] = ui.tab(tab_name)
    with ui.tab_panels(tabs, value=tab_dict[DEFAULT_TAB]).classes('w-full'):
        for tab_name, tab in tab_dict.items():
            ui_fun = SUB_UI_FUNS[tab_name]
            with ui.tab_panel(tab):
                ui_fun()

#display_target_component_ui()
display_ui()
ui.run()
