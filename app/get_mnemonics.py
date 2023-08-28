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


# =========
# Dataclass
# =========
@dataclass
class TCConcepts:
    """
    Associate a target concept (to learn,) with component concepts (available
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
class SessionData:
    displayed_result_idx: Optional[int]


# =============
# Other classes
# =============
@dataclass
class TCResult:
    """Generation result for Target/Component mnemonic"""
    tc_concepts: TCConcepts
    mnemonic: GeneratedText
    revisions: list[GeneratedText] = field(default_factory=list) 

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


# ===============
# Page components
# ===============
def concept_inputation_ui(concepts: TCConcepts)-> None:
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
            if position is None:
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
        on_change=partial(update_concept, concepts=concepts,
        concept_type="target", position=None)
    )
    ui.label("Related concepts")
    # Inputation of related concepts
    for i in range(N_COMPONENT_CONCEPTS):
        ui.input(
            on_change=partial(update_concept, concepts=concepts,
            concept_type="component", position=i)
        )

def mnemonic_generation_ui(
    concepts: TCConcepts,
    results: TCResults,
    pure_concepts_template: Template,
    revision_template: Template,
    session_data: SessionData,
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
        output = generate_gpt4_simple(prompt = pure_concepts_prompt)
        # Storing everything
        result = TCResult(tc_concepts=concepts, mnemonic=output)
        results.add_result(result)
        # Point to the last result
        session_data.displayed_result_idx = results.len() - 1
        # Dipslay
        prompt_md.set_content(ms_text.replace_linebreaks_w_br(pure_concepts_prompt))
        #mnemonic_md.set_content(ms_text.replace_linebreaks_w_br(result.mnemonic))
        # Enable revision
        revision_button.set_visibility(True)

    def act_on_click_revise(results: TCResults):
        pass

    # Button for generation
    ui.button(
        text="Generate",
        icon="toys",
        on_click=partial(act_on_click_generate, concepts=concepts,
                         results=results,
                         pure_concepts_template=pure_concepts_template)
    )
    # Slot for error if something is missing
    concept_error_label = ui.label()
    # Prompt
    prompt_md = ui.markdown()
    # Generated mnemonic ; show the one pointed at in app.storage.user
    mnemonic_md = ui.markdown()
    mnemonic_md.bind_content_from(
        session_data,
        "displayed_result_idx",
        backward=lambda idx: "" if idx is None else results.get_result(idx=idx).mnemonic
    )
    # Button for revision
    revision_button = ui.button(
        "Revise",
        on_click=partial(
            act_on_click_revise, results=results
        )
    )
    if mnemonic_md.content == "":
        revision_button.set_visibility(False)
    


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
    session_data = SessionData(displayed_result_idx=None)
    # Initialize Concepts object
    concepts = TCConcepts(
        target_concept="",
        component_concepts=["" for _ in range(N_COMPONENT_CONCEPTS)],
    )
    # Initialize Results object
    results = TCResults()
    # Display UI
    concept_inputation_ui(concepts=concepts)
    mnemonic_generation_ui(
        concepts = concepts,
        results=results,
        pure_concepts_template=pure_concepts_template,
        revision_template=revision_template,
        session_data=session_data,
    )
# Rendering
main_ui()
ui.run(storage_secret=STORAGE_SECRET)
