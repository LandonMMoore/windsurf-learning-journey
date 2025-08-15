from typing import Dict

from langchain.output_parsers import PydanticOutputParser

from src.schema.report_schema import FormulaAgentResponse
from src.services.sub_report_service import SubReportService


class FormulaOutputParser:
    """
    LangChain output parser to extract formula and explanation from agent responses.
    """

    def __init__(self, sub_report_service: SubReportService):
        self.sub_report_service = sub_report_service
        self.parser = PydanticOutputParser(pydantic_object=FormulaAgentResponse)

    def parse_response(self, response: str) -> Dict[str, str]:
        try:
            parsed = self.parser.parse(response)

            # self.sub_report_service.validate_formula(parsed.formula)

            return {"formula": parsed.formula, "explanation": parsed.explanation}
        except Exception:
            return {"formula": "", "explanation": response.strip()}

    def get_format_instructions(self) -> str:
        """Get format instructions for the LLM"""
        return self.parser.get_format_instructions()
