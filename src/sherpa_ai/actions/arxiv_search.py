from typing import Any

from sherpa_ai.actions.base import BaseRetrievalAction
from sherpa_ai.tools import SearchArxivTool


SEARCH_SUMMARY_DESCRIPTION = """Role Description: {role_description}
Task: {task}

Relevant Paper Title and Summary:
{paper_title_summary}


Review and analyze the provided paper summary with respect to the task. Craft a concise and short, unified summary that distills key information that is most relevant to the task, incorporating reference links within the summary.
Only use the information given. Do not add any additional information. The summary should be less than {n} setences
"""  # noqa: E501


class ArxivSearch(BaseRetrievalAction):
    role_description: str
    task: str
    llm: Any  # The BaseLanguageModel from LangChain is not compatible with Pydantic 2 yet
    description: str = SEARCH_SUMMARY_DESCRIPTION
    max_results: int = 5
    _search_tool: Any

    # Override the name and args from BaseAction
    name: str = "ArxivSearch"
    args: dict = {"query": "string"}
    usage: str = "Search paper on the Arxiv website"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_tool = SearchArxivTool()

    def execute(self, query) -> str:
        result, resources = self._search_tool._run(query, return_resources=True)
        self.add_resources(resources)

        prompt = self.description.format(
            task=self.task,
            paper_title_summary=result,
            n=self.max_results,
            role_description=self.role_description,
        )

        result = self.llm.predict(prompt)

        return result
