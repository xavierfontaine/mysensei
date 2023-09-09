from typing import Annotated

ComponentConcept = Annotated[str, "Concept used to recall the target concept"]
TargetConcept = Annotated[str, "Concept to recall"]
GeneratedText = Annotated[str, "Generated text"]
PromptParamName = Annotated[str, "Field name in a prompt"]
Prompt = Annotated[str, "Prompt"]
