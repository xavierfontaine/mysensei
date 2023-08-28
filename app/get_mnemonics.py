from nicegui import ui
from nicegui.events import ValueChangeEventArguments
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, Template
from functools import partial
from typing import Literal, Optional

from mysensei import text as ms_text
from mysensei import io as ms_io



# =============
# Load template
# =============


# ===========
# Annotations
# ===========
from typing import Annotated
ComponentConcept = Annotated[str, "Concept used to recall the target concept"]
TargetConcept = Annotated[str, "Concept to recall"]


# =========
# Constants
# =========
N_COMPONENT_CONCEPTS = 4


# =========
# Dataclass
# =========
@dataclass
class Concepts:
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


# ===========
# Other class
# ===========



# ===============
# Page components
# ===============
def concept_inputation_ui(concepts: Concepts)-> None:
    """UI for inputing the Target and Related Concepts"""
    # Defining update mechanism for concepts
    def update_concept(
        event: ValueChangeEventArguments,
        concepts: Concepts,
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
    concepts: Concepts,
    pure_concepts_template: Template,
):
    # TODO: docstr

    # Action on click
    def act_on_click(
        concepts: Concepts,
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
        # Render the template
        print(concepts.nonempty_component_concepts())
        pure_concepts_prompt = pure_concepts_template.render(
            target_concept = concepts.target_concept,
            component_concepts = concepts.nonempty_component_concepts(),
        )
        # Display
        prompt_md.set_content(ms_text.replace_linebreaks_w_br(pure_concepts_prompt))
        return
        # OpenAI completion (TODO: clean)
        from mysensei.generation import openai
        completion = openai.ChatCompletion.create(
          model="gpt-4",
          messages=[
            {"role": "user", "content": pure_concepts_prompt},
          ]
        )
        output = completion.choices[0].message.content
        mnemonic_md.set_content(ms_text.replace_linebreaks_w_br(output))
    # Button for generation
    ui.button(
        text="Generate",
        icon="toys",
        on_click=partial(act_on_click, concepts=concepts,
                         pure_concepts_template=pure_concepts_template)
    )
    # Slot for error if something is missing
    concept_error_label = ui.label()

    # Prompt
    prompt_md = ui.markdown()

    # Generated mnemonic
    mnemonic_md = ui.markdown()


# ================
# Page composition
# ================
@ui.page("/")
def main_ui()-> None:
    # Load template
    ## TODO: put the template at the direct module scope? (loaded only once per
    ## server loading)
    pure_concepts_template = ms_io.get_jinja_template(template_name="pure_concepts", version = 0)
    # Initialize Concepts object
    concepts = Concepts(
        target_concept="",
        component_concepts=["" for _ in range(N_COMPONENT_CONCEPTS)],
    )
    # Display UI
    concept_inputation_ui(concepts=concepts)
    mnemonic_generation_ui(
        concepts = concepts,
        pure_concepts_template=pure_concepts_template,
    )
# Rendering
main_ui()
ui.run()
