import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from lark import Lark, Tree, Visitor
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    constr,
    field_serializer,
    field_validator,
    model_validator,
)

from src.model.master_model import (
    MasterAward,
    MasterCostCenter,
    MasterFund,
    MasterParentTask,
    MasterProgram,
    MasterProjectDetails,
    MasterSponsor,
    MasterSubTask,
    MasterTransaction,
)
from src.model.report_model import ScheduleReportRerunPeriod
from src.schema.base_schema import FindBase, FindResult, ModelBaseInfo, SearchOptions
from src.util.get_fields_from_models import get_original_table_name
from src.util.schema import make_optional

logger = logging.getLogger(__name__)

FUNCTION_REGISTRY = {
    "SUM": {"min_args": 1, "max_args": None, "arg_types": "number"},
    "AVERAGE": {"min_args": 1, "max_args": None, "arg_types": "number"},
    "MOD": {"min_args": 2, "max_args": 2, "arg_types": ["number", "number"]},
    "ROUND": {"min_args": 2, "max_args": 2, "arg_types": ["number", "number"]},
    "CEIL": {"min_args": 1, "max_args": 1, "arg_types": ["number"]},
    "FLOOR": {"min_args": 1, "max_args": 1, "arg_types": ["number"]},
    "LOG": {"min_args": 1, "max_args": 1, "arg_types": ["number"]},
    "SQRT": {"min_args": 1, "max_args": 1, "arg_types": ["number"]},
    "POWER": {"min_args": 2, "max_args": 2, "arg_types": ["number", "number"]},
    "ABS": {"min_args": 1, "max_args": 1, "arg_types": ["number"]},
    "MAX": {"min_args": 1, "max_args": None, "arg_types": "number"},
    "MIN": {"min_args": 1, "max_args": None, "arg_types": "number"},
    "DATEDIFF": {
        "min_args": 3,
        "max_args": 3,
        "arg_types": ["string", {"date", "datetime"}, {"date", "datetime"}],
    },
    "DATEPART": {
        "min_args": 2,
        "max_args": 2,
        "arg_types": ["string", {"date", "datetime"}],
    },
    "DATEADD": {
        "min_args": 3,
        "max_args": 3,
        "arg_types": ["string", "number", {"date", "datetime"}],
    },
    "TODAY": {"min_args": 0, "max_args": 0, "arg_types": []},
    "IF": {"min_args": 3, "max_args": 3, "arg_types": ["boolean", "any", "any"]},
}

NO_ARGUMENT_FUNCTIONS = {"TODAY"}

FORMULA_GRAMMAR = r"""
field: "{" (UUID | CNAME "." CNAME) "}" -> field

?start: expr

?expr: logical_expr

?logical_expr: comparison_expr
             | logical_expr "AND" comparison_expr   -> and_expr
             | logical_expr "OR" comparison_expr    -> or_expr

?comparison_expr: sum_expr
                | sum_expr "==" sum_expr            -> eq
                | sum_expr "!=" sum_expr            -> ne
                | sum_expr "<" sum_expr             -> lt
                | sum_expr "<=" sum_expr            -> le
                | sum_expr ">" sum_expr             -> gt
                | sum_expr ">=" sum_expr            -> ge

?sum_expr: term
         | sum_expr "+" term                        -> add
         | sum_expr "-" term                        -> sub

?term: factor
     | term "*" factor                              -> mul
     | term "/" factor                              -> div

?factor: atom_base

?atom_base: field
     | NUMBER               -> number
     | STRING               -> string
     | "None"               -> none
     | "none"               -> none
     | "Null"               -> none
     | "null"               -> none
     | function_call
     | "(" expr ")"

function_name: CNAME

function_call: function_name "(" [arguments] ")"      -> function_call

arguments: expr ("," expr)*

signed_number: SIGNED_NUMBER -> number

SIGNED_NUMBER: /[-+]?\d+(\.\d+)?/

STRING: ESCAPED_STRING | /'(?:\\'|[^'])*'/
UUID.2: /[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/

%import common.CNAME
%import common.ESCAPED_STRING
%import common.NUMBER
%import common.WS
%ignore WS
"""


LARK_PARSER = Lark(
    FORMULA_GRAMMAR,
    parser="lalr",
    lexer="contextual",
    start="start",
)

MODEL_REGISTRY: Dict[str, object] = {
    "master_project_details": MasterProjectDetails,
    "master_parent_tasks": MasterParentTask,
    "master_sub_tasks": MasterSubTask,
    "master_transactions": MasterTransaction,
    "master_awards": MasterAward,
    "master_funds": MasterFund,
    "master_sponsors": MasterSponsor,
    "master_cost_centers": MasterCostCenter,
    "master_programs": MasterProgram,
}


OPERATOR_DATA_TYPE_MAP: Dict[str, set[str]] = {
    "equals": set(
        [
            "string",
            "str",
            "number",
            "int",
            "float",
            "boolean",
            "bool",
            "date",
            "datetime",
        ]
    ),
    "not_equals": set(
        [
            "string",
            "str",
            "number",
            "int",
            "float",
            "boolean",
            "bool",
            "date",
            "datetime",
        ]
    ),
    "in": set(
        [
            "string",
            "str",
            "number",
            "int",
            "float",
            "boolean",
            "bool",
            "date",
            "datetime",
        ]
    ),
    "not_in": set(
        [
            "string",
            "str",
            "number",
            "int",
            "float",
            "boolean",
            "bool",
            "date",
            "datetime",
        ]
    ),
    "starts_with": set(["string", "str"]),
    "ends_with": set(["string", "str"]),
    "contains": set(["string", "str"]),
    "less_than": set(["number", "int", "float", "date", "datetime"]),
    "less_than_or_equal": set(["number", "int", "float", "date", "datetime"]),
    "greater_than": set(["number", "int", "float", "date", "datetime"]),
    "greater_than_or_equal": set(["number", "int", "float", "date", "datetime"]),
    "range": set(["number", "int", "float", "date", "datetime"]),
    "is_null": set(
        [
            "string",
            "str",
            "number",
            "int",
            "float",
            "boolean",
            "bool",
            "date",
            "datetime",
        ]
    ),
    "is_not_null": set(
        [
            "string",
            "str",
            "number",
            "int",
            "float",
            "boolean",
            "bool",
            "date",
            "datetime",
        ]
    ),
}


def extract_formula_dependencies(expression: str) -> set[UUID]:
    return {UUID(match) for match in re.findall(r"\{([0-9a-fA-F-]{36})\}", expression)}


def build_dependency_graph(config_list) -> dict[UUID, set[UUID]]:
    uuid_set = {field.uuid for field in config_list}
    graph = {}

    for field in config_list:
        if field.type == "formula":
            refs = extract_formula_dependencies(field.expression)
            invalid_refs = refs - uuid_set
            if invalid_refs:
                raise ValueError(
                    f"Formula field '{field.label}' ({field.uuid}) references unknown UUID(s): {', '.join(str(r) for r in invalid_refs)}"
                )
            graph[field.uuid] = refs
        else:
            graph[field.uuid] = set()
    return graph


def detect_cycles(graph: dict[UUID, set[UUID]]):
    visited = set()
    rec_stack = set()

    def dfs(node):
        if node not in visited:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited and dfs(neighbor):
                    return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
        return False

    for node in graph:
        if dfs(node):
            raise ValueError(f"Circular reference detected involving UUID: {node}")


class FormulaFieldValidator(Visitor):
    def __init__(self):
        self.alias_map = MODEL_REGISTRY
        self.fields_used = []
        self.value_types = {}

    def get_field_type(self, model, column_name: str) -> str:
        try:
            field_type = getattr(model, column_name).type.python_type
        except Exception as e:
            raise ValueError(f"Unable to resolve field type for '{column_name}': {e}")

        if field_type in (int, float):
            return "number"
        if field_type is bool:
            return "boolean"
        if field_type.__name__.lower() in ("date", "datetime"):
            return "date"
        if field_type is str:
            return "string"

        raise ValueError(f"Unsupported field type: {field_type}")

    def get_function_type(self, func_name: str, args: list[Tree]) -> str:
        if func_name in {
            "SUM",
            "AVERAGE",
            "MOD",
            "ROUND",
            "CEIL",
            "FLOOR",
            "LOG",
            "SQRT",
            "POWER",
            "ABS",
            "MAX",
            "MIN",
            "DATEDIFF",
            "DATEPART",
        }:
            return "number"
        elif func_name in {"DATEADD", "TODAY"}:
            return "date"
        elif func_name == "IF":
            return self.value_types[id(args[1])]
        else:
            raise ValueError(f"Invalid function: {func_name}")

    def eq(self, tree):
        self.value_types[id(tree)] = "boolean"

    def ne(self, tree):
        self.value_types[id(tree)] = "boolean"

    def lt(self, tree):
        self.value_types[id(tree)] = "boolean"

    def le(self, tree):
        self.value_types[id(tree)] = "boolean"

    def gt(self, tree):
        self.value_types[id(tree)] = "boolean"

    def ge(self, tree):
        self.value_types[id(tree)] = "boolean"

    def and_expr(self, tree):
        self.value_types[id(tree)] = "boolean"

    def or_expr(self, tree):
        self.value_types[id(tree)] = "boolean"

    def add(self, tree):
        self.value_types[id(tree)] = "number"

    def sub(self, tree):
        self.value_types[id(tree)] = "number"

    def mul(self, tree):
        self.value_types[id(tree)] = "number"

    def div(self, tree):
        self.value_types[id(tree)] = "number"

    def number(self, tree):
        self.value_types[id(tree)] = "number"

    def string(self, tree):
        self.value_types[id(tree)] = "string"

    def none(self, tree):
        self.value_types[id(tree)] = "any"

    def field(self, tree):
        if len(tree.children) == 1:
            uuid_token = tree.children[0]
            try:
                UUID(uuid_token.value)
            except ValueError:
                raise ValueError(f"Invalid UUID reference: {uuid_token.value}")
            # TODO: Add UUID type to the value_types.
            # UUID are referenced formulas, so we need to handle them differently.
            self.value_types[id(tree)] = "UUID"
            return
        if len(tree.children) != 2:
            raise ValueError(
                "Invalid field format, expected {{table.column}} or {{uuid}}"
            )

        table_name = get_original_table_name(tree.children[0].value)
        column_name = tree.children[1].value

        if table_name not in MODEL_REGISTRY:
            raise ValueError(f"Unknown table '{table_name}' in formula")

        model = MODEL_REGISTRY[table_name]
        if not hasattr(model, column_name):
            raise ValueError(f"Field '{table_name}.{column_name}' is not valid")

        col_type = self.get_field_type(model, column_name)
        self.fields_used.append((table_name, column_name))
        self.value_types[id(tree)] = col_type

    def function_call(self, tree: Tree):

        func_name_tree = tree.children[0]  # e.g., Tree('SUM_FN', [])

        if (
            func_name_tree.data == "function_name"
            and func_name_tree.children[0].value not in FUNCTION_REGISTRY
        ):
            raise ValueError(
                f"Unsupported function: {func_name_tree.children[0].value}"
            )
        func_name = func_name_tree.children[0].value

        args = []
        if (
            len(tree.children) > 1
            and isinstance(tree.children[1], Tree)
            and tree.children[1].data == "arguments"
        ):
            args = tree.children[1].children

        func_info = FUNCTION_REGISTRY[func_name]
        min_args = func_info["min_args"]
        max_args = func_info["max_args"]
        expected_arg_types = func_info["arg_types"]

        actual_arg_count = len(args)
        if actual_arg_count < min_args:
            raise ValueError(
                f"Function '{func_name}' expects at least {min_args} arguments, got {actual_arg_count}"
            )
        if max_args is not None and actual_arg_count > max_args:
            raise ValueError(
                f"Function '{func_name}' expects at most {max_args} arguments, got {actual_arg_count}"
            )

        if func_name in {"DATEADD", "DATEDIFF", "DATEPART"}:
            # First argument must be a literal string
            part_arg = args[0]
            if isinstance(part_arg, Tree) and part_arg.data == "string":
                valid_parts = {
                    "year",
                    "yy",
                    "yyyy",
                    "quarter",
                    "qq",
                    "month",
                    "mm",
                    "dayofyear",
                    "dy",
                    "day",
                    "dd",
                    "week",
                    "wk",
                    "weekday",
                    "dw",
                    "hour",
                    "hh",
                    "minute",
                    "mi",
                    "second",
                    "ss",
                    "millisecond",
                    "ms",
                    "microsecond",
                    "mcs",
                    "nanosecond",
                    "ns",
                }

                part_value = part_arg.children[0].value.strip("'\"").lower()
                if part_value not in valid_parts:
                    raise ValueError(
                        f"Invalid date part '{part_value}' in '{func_name}'. Must be one of: {', '.join(sorted(valid_parts))}"
                    )

        if func_name == "IF":
            arg_2_type = self.value_types[id(args[1])]
            arg_3_type = self.value_types[id(args[2])]
            # If the arguments are not UUIDs, they must be of the same type.
            if "UUID" not in [arg_2_type, arg_3_type] and arg_2_type != arg_3_type:
                raise ValueError(
                    f"Function '{func_name}' argument 2 and 3 must be of the same type"
                )
        func_return_type = self.get_function_type(func_name, args)
        self.value_types[id(tree)] = func_return_type

        for i, arg in enumerate(args):
            arg_type = self.value_types.get(id(arg))
            # TODO: Add validation for UUIDs.
            if arg_type == "UUID":
                continue
            if (
                (
                    isinstance(expected_arg_types[i], str)
                    and expected_arg_types[i] in {"date", "datetime"}
                )
                or (
                    isinstance(expected_arg_types[i], set)
                    and (
                        "date" in expected_arg_types[i]
                        or "datetime" in expected_arg_types[i]
                    )
                )
                and arg_type == "string"
            ):
                allowed_formats = [
                    "%Y-%m-%d",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M:%S.%f",
                    "%Y-%m-%d %H:%M:%S.%f%z",
                ]
                raw = arg.children[0].value.strip("'").strip('"')
                for format in allowed_formats:
                    try:
                        datetime.strptime(raw, format)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError(
                        f"Invalid date format in '{func_name}' argument {i+1}: {raw}"
                    )
            elif isinstance(expected_arg_types, str):
                if expected_arg_types != "any" and arg_type != expected_arg_types:
                    raise ValueError(
                        f"Function '{func_name}' argument {i+1} expects type '{expected_arg_types}', got '{arg_type}'"
                    )
            elif isinstance(expected_arg_types, set):
                if arg_type not in expected_arg_types:
                    raise ValueError(
                        f"Function '{func_name}' argument {i+1} expects type '{expected_arg_types}', got '{arg_type}'"
                    )
            elif isinstance(expected_arg_types, list):
                if expected_arg_types[i] != "any" and not (
                    (
                        isinstance(expected_arg_types[i], set)
                        and arg_type in expected_arg_types[i]
                    )
                    or (
                        isinstance(expected_arg_types[i], str)
                        and arg_type == expected_arg_types[i]
                    )
                ):
                    raise ValueError(
                        f"Function '{func_name}' argument {i+1} expects type '{expected_arg_types[i]}', got '{arg_type}'"
                    )
            else:
                raise ValueError(f"Invalid argument type: {expected_arg_types}")

        # Recursively validate each argument
        for arg in args:
            if isinstance(arg, Tree):
                self.visit(arg)


class ReportFieldConfig(BaseModel):
    uuid: UUID
    label: constr(strip_whitespace=True, min_length=1)
    type: Literal[
        "field",
        "formula",
        "string",
        "number",
        "date",
        "boolean",
        "datetime",
        "integer",
        "float",
    ]
    expression: constr(strip_whitespace=True, min_length=1)
    group_by_aggregate: Optional[Literal["sum", "avg", "min", "max", "count"]] = Field(
        ..., description="Required field; can be null"
    )
    chat_id: Optional[int] = Field(default=None)
    metadata: Optional[Any] = Field(default=None)

    @field_serializer("uuid")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)

    @model_validator(mode="before")
    def validate_expression(cls, values):
        expr_type = values["type"]
        expr = values["expression"]

        if expr_type != "formula":
            EXPR_PATTERN = re.compile(r"\{(?P<table>\w+)\.(?P<column>\w+)\}")
            match = EXPR_PATTERN.fullmatch(expr)
            if not match:
                raise ValueError(
                    f"Invalid field format: {expr}, expected format: {{table.column}}"
                )

            table_name = get_original_table_name(match["table"])
            column_name = match["column"]

            if table_name not in MODEL_REGISTRY:
                raise ValueError(f"Unknown table '{table_name}' in formula")
            model = MODEL_REGISTRY[table_name]
            if not hasattr(model, column_name):
                raise ValueError(f"Field '{table_name}.{column_name}' is not valid")

        else:
            try:
                tree = LARK_PARSER.parse(expr)
                visitor = FormulaFieldValidator()
                visitor.visit(tree)
            except Exception as e:
                logger.error("Invalid formula", exc_info=True)
                raise ValueError(f"Invalid formula: {str(e)}")

        return values


class FieldCondition(BaseModel):
    field: str
    operator: Literal[
        "equals",
        "not_equals",
        "in",
        "not_in",
        "less_than",
        "less_than_or_equal",
        "greater_than",
        "greater_than_or_equal",
        "starts_with",
        "ends_with",
        "contains",
        "range",
        "is_null",
        "is_not_null",
    ]
    value: Optional[Union[str, int, float, List[Union[str, int, float]]]] = None

    @model_validator(mode="after")
    def validate_operator_logic(self):
        op = self.operator
        val = self.value
        if op in {"equals", "not_equals", "starts_with"}:
            if isinstance(val, list) or val is None:
                raise ValueError(f"`value` must be a single non-null value for `{op}`")
        elif op in {"in", "not_in"}:
            if not isinstance(val, list):
                raise ValueError(f"`value` must be a list for `{op}`")
        if op in {
            "less_than",
            "less_than_or_equal",
            "greater_than",
            "greater_than_or_equal",
        }:
            if not isinstance(val, (int, float)):
                raise ValueError(f"`value` must be a number for `{op}`")
        elif op == "range":
            if not isinstance(val, list) or len(val) != 2:
                raise ValueError(f"`value` must be a list of two values for `{op}`")
            if not all(isinstance(v, (int, float)) for v in val):
                raise ValueError(f"`value` must be a list of two numbers for `{op}`")
        elif op in {"is_null", "is_not_null"}:
            if isinstance(val, bool):
                raise ValueError(f"`value` must true or false for `{op}`")
        return self


class LogicalCondition(BaseModel):
    logical_operator: Literal["and", "or"]
    conditions: List["Condition"]


Condition = Union[FieldCondition, LogicalCondition]
LogicalCondition.model_rebuild()


class ReportFilter(BaseModel):
    filters: Optional[LogicalCondition] = None

    @field_validator("filters", mode="before")
    def allow_empty_dict(cls, v):
        # If the filters is empty, return None
        if not v:
            return None
        return v


class ReportFind(FindBase, ReportFilter): ...


def validate_filter_uuids(
    condition: Union[FieldCondition, LogicalCondition], valid_uuids: set[str]
):
    if isinstance(condition, FieldCondition):
        if condition.field not in valid_uuids:
            raise ValueError(f"Condition refers to unknown UUID: {condition.field}")
    elif isinstance(condition, LogicalCondition):
        for cond in condition.conditions:
            validate_filter_uuids(cond, valid_uuids)


class SubReportConfigBaseSchema(ReportFilter):
    config: List[ReportFieldConfig]
    group_by: Optional[list[str]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_ids_and_formulas(cls, values):
        config_list = values.config
        seen_ids = set()

        # 1. Check for duplicate UUIDs
        for item in config_list:
            uuid_str = str(item.uuid)
            if uuid_str in seen_ids:
                raise ValueError(f"Duplicate ReportFieldConfig uuid found: {uuid_str}")
            seen_ids.add(uuid_str)

        # 2. Build dependency graph & check references
        graph = build_dependency_graph(config_list)

        # 3. Check for circular dependencies
        detect_cycles(graph)

        if values.filters:
            validate_filter_uuids(values.filters, seen_ids)

        for uuid in values.group_by:
            if uuid not in seen_ids:
                raise ValueError(
                    f"Group by field '{uuid}' not found in config. Please check the group_by field."
                )

        if values.group_by:
            for item in config_list:
                if str(item.uuid) in values.group_by:
                    continue
                if not item.group_by_aggregate:
                    raise ValueError(
                        f"Field '{item.label}' either must be in group_by or have a group_by_aggregate."
                    )

        return values


class SubReportBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: SubReportConfigBaseSchema


class SubReportCreate(SubReportBase):
    report_configuration_id: int


class SubReportInfo(ModelBaseInfo, SubReportCreate):
    model_config = ConfigDict(from_attributes=True)
    pass


class SubReportUpdate(make_optional(SubReportBase)):
    pass


class ReportConfigBaseSchema(BaseModel):
    name: str
    description: Optional[str] = None
    schedule_rerun_period: Optional[ScheduleReportRerunPeriod] = None
    template_id: Optional[int] = None
    chat_id: Optional[int] = None


class ReportConfigurationCreateSchema(ReportConfigBaseSchema):
    tags: Optional[list[int]] = None
    chat_id: Optional[int] = None
    model_config = ConfigDict(use_enum_values=True, validate_default=True)


class ReportConfigurationCreateSchemaTool(ReportConfigBaseSchema):
    tags: Optional[list[str]] = None
    model_config = ConfigDict(use_enum_values=True, validate_default=True)


class ReportConfigurationTagSchema(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class ReportConfigurationResponseSchema(ReportConfigBaseSchema, ModelBaseInfo):
    created_by_id: int
    chat_id: Optional[int] = None
    tags: Optional[list[ReportConfigurationTagSchema]] = None
    sub_reports: Optional[list[SubReportInfo]] = None

    model_config = ConfigDict(from_attributes=True)


class ReportConfigurationUpdateSchema(make_optional(ReportConfigurationCreateSchema)):
    chat_id: Optional[int] = None


class ReportConfigurationUpdateSchemaTool(
    make_optional(ReportConfigurationCreateSchema)
):
    tags: Optional[list[str]] = None
    model_config = ConfigDict(use_enum_values=True, validate_default=True)


class ReportConfigurationFind(make_optional(FindBase)):
    name: Optional[str] = None
    schedule_rerun_period: Optional[ScheduleReportRerunPeriod] = None


class ReportConfigurationListResponseSchema(ReportConfigBaseSchema, ModelBaseInfo):
    created_by_id: int
    chat_id: Optional[int] = None
    tags: Optional[list[ReportConfigurationTagSchema]] = None

    model_config = ConfigDict(from_attributes=True)


class ReportConfigurationListResponse(FindResult):
    founds: Optional[List[ReportConfigurationListResponseSchema]] = None
    search_options: Optional[SearchOptions] = None


class ReportFieldsFind(BaseModel):
    ordering: Optional[str] = None
    search: Optional[str] = None


ValidSchema = Literal[
    "master_funds",
    "master_programs",
    "master_cost_centers",
    "master_accounts",
    "master_project_details",
    "master_awards",
    "master_sponsors",
    "master_parent_tasks",
    "master_sub_tasks",
    "master_transactions",
]


class SharedDataFind(FindBase):
    """Schema for searching and filtering shared data from master tables."""

    pass


LogicalOperator = Literal["AND", "OR"]
AllOperators = Literal["equals", "not_equals", "in", "not_in", "starts_with", "range"]


class FilterCondition(BaseModel):
    field: Optional[str]
    operator: AllOperators
    value: Optional[Union[str, int, float, List[Union[str, int, float]]]] = None
    start: Optional[Union[int, float, str]] = None
    end: Optional[Union[int, float, str]] = None

    @model_validator(mode="after")
    def validate_operator_logic(self) -> "FilterCondition":
        op = self.operator
        val = self.value
        if op in {"equals", "not_equals", "starts_with"}:
            if isinstance(val, list) or val is None:
                raise ValueError(f"`value` must be a single non-null value for `{op}`")
        elif op in {"in", "not_in"}:
            if not isinstance(val, list):
                raise ValueError(f"`value` must be a list for `{op}`")
        elif op == "range":
            if self.start is None or self.end is None:
                raise ValueError("Both `start` and `end` are required for `range`")
        return self


class FilterGroup(BaseModel):
    operator: LogicalOperator
    conditions: List[Union["FilterGroup", FilterCondition]]

    @field_validator("conditions")
    @classmethod
    def validate_conditions(cls, v):
        if not v:
            raise ValueError("`conditions` must be a non-empty list")
        return v


# Allow recursive reference
FilterGroup.model_rebuild()


class SearchPayload(BaseModel):
    fields: List[str]
    value: Union[str, int, float]


class SortCondition(BaseModel):
    field: str
    order: Literal["asc", "desc"]


class ReportConfigurationQueryElasticsearch(BaseModel):
    index: str
    search: Optional[SearchPayload] = None
    filter: Optional[FilterGroup] = None
    page: Optional[int] = Field(default=1, ge=1)
    page_size: Optional[int] = Field(default=15, ge=1)
    sort: Optional[List[SortCondition]] = None


class ReportFunctionResponse(BaseModel):
    category: str
    sub_category: str
    display_name: str
    description: str
    example: str


# Agent schema
class ChatRequest(BaseModel):
    query: str
    chat_id: Optional[int] = None
    message_id: Optional[int] = Field(default=None)
    report_id: Optional[int] = Field(default=None)


class ChatResponse(BaseModel):
    response: str
    chat_id: int
    message_id: int


class FormulaAssistantChatRequest(BaseModel):
    query: str
    chat_id: Optional[int] = None
    message_id: Optional[int] = Field(default=None)
    sub_report_id: Optional[int] = None

    @field_validator("query")
    def validate_query(cls, v):
        if len(v) > 1000:
            raise ValueError(
                "Input query is too long, it must be less than 250 characters"
            )

        combined_pattern = re.compile(
            r"(system:|assistant:|user:|role:|content:|"
            r"ignore previous|ignore above|forget everything|"
            r"you are now|act as|pretend to be|"
            r"_source|_index|_id|_score|_shards|"
            r"settings|mappings|analyzer|tokenizer|"
            r"provide\s+(the\s+)?credentials|"
            r"(access|admin|login|password|username)\s+(to|for)\s+(your\s+)?(database|system|account)|"
            r"give\s+me\s+access|"
            r"bypass\s+(authentication|security|rules|restrictions|limitations)|"
            r"disable\s+security|"
            r"auth\s*token|api[_-]?key|secret[_-]?key|authorization\s*header|"
            r"follow\s+my\s+orders|"
            r"do\s+not\s+consider\s+(any\s+)?rules|"
            r"strictly\s+bypass|"
            r"ignore\s+(all\s+)?(rules|restrictions|limitations))",
            re.IGNORECASE,
        )

        if combined_pattern.search(v):
            logger.warning(
                f"EDS Formula Assistant Query contains potentially malicious content: {v}"
            )
            raise ValueError("Query contains potentially malicious content")

        return v.strip()


class FormulaAgentResponse(BaseModel):
    formula: str = Field(
        description="The generated formula (empty string if no formula)"
    )
    explanation: str = Field(
        description="Explanation of the formula or response message"
    )


class FormulaAssistantResponse(FormulaAgentResponse):
    chat_id: int
    message_id: int


class ChatHistory(BaseModel):
    id: str = Field(alias="_id")
    user_query: str
    message_id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime


class ChatHistoryResponse(ChatHistory):
    feedback: Optional[Literal["like", "dislike", "null"]] = None
    response: str


class FormulaAssistantChatHistoryResponse(ChatHistory):
    response: Optional[dict] = None

class ValidateFormula(BaseModel):
    formula: str


class MasterModelUniqueValues(FindBase):
    schema_name: str = Field(..., description="Schema name")
    field_name: str = Field(..., description="Field name to extract unique values for")


class ReportAgentResponseFeedback(BaseModel):
    chat_id: int
    message_id: int
    feedback: Literal["like", "dislike", "null"]
