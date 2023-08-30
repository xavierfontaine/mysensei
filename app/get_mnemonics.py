from nicegui import app, ui
from nicegui.events import ValueChangeEventArguments
from dataclasses import dataclass, field
from jinja2 import Environment, FileSystemLoader, Template
from functools import partial
from typing import Literal, Optional

from mysensei import text as ms_text
from mysensei import io as ms_io
from mysensei.generation import generate_gpt4_simple


# ===========
# Annotations
# ===========
from typing import Annotated
ComponentConcept = Annotated[str, "Concept used to recall the target concept"]
TargetConcept = Annotated[str, "Concept to recall"]
GeneratedText = Annotated[str, "Generated text"]


# =========
# Constants
# =========
N_COMPONENT_CONCEPTS = 4
STORAGE_SECRET = ms_io.get_conf_toml("secrets.toml")["cookies"]["storage_secret"]
# For testing (replaces GPT4 with some text)
MOCK_GPT4 = False


# =========
# Dataclass
# =========
@dataclass
class TCConcepts:
    """
    Associate a Target concept (to learn,) with Component concepts (available
    at the time of recall.)
    """
    target_concept: TargetConcept
    component_concepts: list[ComponentConcept]

    def no_target_concept(self)->bool:
        return (self.target_concept == "")

    def no_component_concept(self)->bool:
        return all(c == "" for c in self.component_concepts)

    def nonempty_component_concepts(self)->list[ComponentConcept]:
        return [c  for c in self.component_concepts if c != ""]

@dataclass
class TCResult:
    """Generation result for Target/Component mnemonic"""
    tc_concepts: TCConcepts
    mnemonic: GeneratedText
    revisions: list[TCConcepts] = field(default_factory=list)

@dataclass
class TCResults:
    """list of generation results"""
    _tc_results: list[TCResult] = field(default_factory=list)

    def add_result(self, tc_result: TCResult)->None:
        """Add by reference"""
        self._tc_results.append(tc_result)

    def get_result(self, idx: int)->TCResult:
        return self._tc_results[idx]

    def len(self)->int:
        return len(self._tc_results)

@dataclass
class SessionData:
    displayed_result_idx: int
    concepts: TCConcepts
    results: TCResults

    def set_displayed_result_idx(self, idx=int):
        self.displayed_result_idx = idx

    # Add a getitem for binding functions to be able to access attributes
    #def __getitem__(self, attribute_name: str):
        #return self.__getattribute__(attribute_name)

# =============
# Other classes
# =============


# ===============
# Page components
# ===============
def concept_inputation_ui(session_data: SessionData)-> None:
    """UI for inputing the Target and Related Concepts"""
    # Defining update mechanism for concepts
    def update_concept(
        event: ValueChangeEventArguments,
        concepts: TCConcepts,
        concept_type: Literal["target", "component"],
        position: Optional[int],
    ) -> None:
        """Modify Concepts by reference"""
        # Target concept
        if concept_type == "target":
            concepts.target_concept = event.value
        # Component concepts
        elif concept_type == "component":
            if position == -1:
                raise ValueError(
                    f"parameter `position` is not set despite {concept_type=}"
                )
            else:
                concepts.component_concepts[position] = event.value
        else:
            raise ValueError(f"{concept_type=} which is not expected.")

    # Inputation of main concept
    ui.label("Target concept")
    target_input = ui.input(
        on_change=partial(update_concept, concepts=session_data.concepts,
        concept_type="target", position=None)
    )
    ui.label("Related concepts")
    # Inputation of related concepts
    for i in range(N_COMPONENT_CONCEPTS):
        ui.input(
            on_change=partial(update_concept, concepts=session_data.concepts,
            concept_type="component", position=i)
        )

def mnemonic_generation_ui(
    session_data: SessionData,
    pure_concepts_template: Template,
    revision_template: Template,
):
    # TODO: docstr
    # Action on click
    def act_on_click_generate(
        concepts: TCConcepts,
        results: TCResults,
        pure_concepts_template: Template,
    )->None:
        # Check there is 1 target and 1+ component concepts. If not, display
        # error. Else, hide error in case was displayed.
        if concepts.no_target_concept():
            concept_error_label.set_visibility(True)
            concept_error_label.set_text("No Target Concept has been set")
            return
        elif concepts.no_component_concept():
            concept_error_label.set_visibility(True)
            concept_error_label.set_text("No Component concept has been set")
            return
        else:
            concept_error_label.set_visibility(False)
        # Generation
        pure_concepts_prompt = pure_concepts_template.render(
            target_concept = concepts.target_concept,
            component_concepts = concepts.nonempty_component_concepts(),
        )
        # OpenAI completion
        if not MOCK_GPT4:
            output = generate_gpt4_simple(prompt = pure_concepts_prompt)
        else:
            output = "Hey there! It a TEST \o/"
        # Storing everything
        result = TCResult(tc_concepts=concepts, mnemonic=output)
        results.add_result(result)
        # Display the last results
        change_displayed_mnem_idx(session_data=session_data, new_idx=results.len() - 1)
        # Dipslay prompt
        prompt_md.set_content(ms_text.replace_linebreaks_w_br(pure_concepts_prompt))
        # Enable revision
        revision_button.set_visibility(True)

    def change_displayed_mnem_idx(session_data: SessionData, new_idx:
                                     int)->None:
        """
        - Change the displayed_mnem_idx
        - Display the mnem
        - Modify the enablement of the navigations arrows
        """
        results_len = session_data.results.len()
        assert (new_idx <= results_len - 1) & (new_idx >= 0), f"{new_idx=}"
        # Change the idx
        session_data.displayed_result_idx = new_idx
        # Display the mnem
        mnemonic_md.set_content(session_data.results.get_result(idx=new_idx).mnemonic)
        # Disable/Enable arrows by cases
        if results_len in [0, 1]:
            back_mnem_icon.set_enabled(False)
            forward_mnem_icon.set_enabled(False)
        # The list has length more than 2
        elif new_idx == 0:
            back_mnem_icon.set_enabled(False)
            forward_mnem_icon.set_enabled(True)
        elif new_idx == results_len - 1:
            back_mnem_icon.set_enabled(True)
            forward_mnem_icon.set_enabled(False)
        else:
            back_mnem_icon.set_enabled(True)
            forward_mnem_icon.set_enabled(True)


    def act_on_click_revise(results: TCResults):
        pass


    # Button for generation
    ui.button(
        text="Generate",
        icon="toys",
        on_click=partial(act_on_click_generate, concepts=session_data.concepts,
                         results=session_data.results,
                         pure_concepts_template=pure_concepts_template)
    )
    # Slot for error if something is missing
    concept_error_label = ui.label()
    # Prompt
    prompt_md = ui.markdown()
    # Generated mnemonic ; show the one pointed at in app.storage.user
    mnemonic_md = ui.markdown()
    #mnemonic_md.bind_content_from(
        #session_data,
        #"displayed_result_idx",
        #backward=lambda idx: "" if idx is None else session_data.results.get_result(idx=idx).mnemonic
    #)
    # Buttons for navigating mnemonics
    back_mnem_icon = ui.button(
        icon="arrow_back",
        on_click=lambda session_data=session_data: change_displayed_mnem_idx(session_data=session_data, new_idx=session_data.displayed_result_idx-1)
        #on_click=lambda session_data=session_data, new_idx=session_data.displayed_result_idx -1 : change_displayed_mnem_idx(session_data=session_data, new_idx=new_idx)
        #on_click=partial(act_on_click_mnemn_arrow, arrow="back", session_data=session_data),
    )
    back_mnem_icon.set_enabled(False)
    forward_mnem_icon = ui.button(
        icon="arrow_forward",
        on_click=lambda session_data=session_data: change_displayed_mnem_idx(session_data=session_data, new_idx=session_data.displayed_result_idx+1)
    )
    forward_mnem_icon.set_enabled(False)
    # Button for revision...
    revision_button = ui.button(
        "Revise",
        on_click=partial(
            act_on_click_revise, results=session_data.results
        )
    )
    # ... shown only if a concept is pointed at
    revision_button.bind_enabled_from(
        session_data,
        "displayed_result_idx",
        backward=lambda idx: idx is not None
    )


# ================
# Page composition
# ================
@ui.page("/")
def main_ui()-> None:
    # Load template
    ## TODO: put the template at the direct module scope? (loaded only once per
    ## server loading)
    pure_concepts_template = ms_io.get_jinja_template(template_name="pure_concepts", version = 0)
    revision_template = ms_io.get_jinja_template(template_name="pure_concepts_revision", version = 0)
    # Intialize session-specific data storage
    session_data = SessionData(
        displayed_result_idx=-1,
        concepts = TCConcepts(
            target_concept="",
            component_concepts=["" for _ in range(N_COMPONENT_CONCEPTS)],
        ),
        results = TCResults()
    )
    # Display UI
    concept_inputation_ui(session_data=session_data)
    mnemonic_generation_ui(
        pure_concepts_template=pure_concepts_template,
        revision_template=revision_template,
        session_data=session_data,
    )
# Rendering
main_ui()
ui.run(storage_secret=STORAGE_SECRET)
