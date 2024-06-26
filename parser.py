from typing import Tuple, List, Any, NamedTuple
import logging

OPS = {
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    "=": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "AND": lambda a, b: a and b,
    "OR": lambda a, b: a or b
}

OP_PRECEDENCE = {
    "=": 4,
    "!=": 4,
    "<": 3,
    ">": 3,
    "AND": 2,
    "OR": 1
}


class Node:
    def __init__(self, value: Any):
        self.left = None
        self.right = None
        self.value = value

    def evaluate(self, row: dict) -> bool:
        raise NotImplementedError()


class BinaryOperator(Node):
    """
    Node representing a binary operator.
    """

    def __init__(self, operator: str, left: Node, right: Node):
        super().__init__(operator)
        self.left = left
        self.right = right

    def evaluate(self, row: dict) -> bool:
        l_result = self.left.evaluate(row)
        r_result = self.right.evaluate(row)
        logging.debug(f"Evaluating {l_result} {self.value} {r_result}")
        return OPS[self.value](l_result, r_result)


class Literal(Node):
    """
    Node representing string/numeric literals.
    """

    def __init__(self, value: Any):
        super().__init__(value)

    def evaluate(self, row: dict) -> bool:
        return self.value


class ColName(Node):
    """
    Node representing column names.
    """

    def __init__(self, value: Any):
        super().__init__(value)

    def evaluate(self, row: dict) -> bool:
        if self.value not in row:
            raise ValueError(f"Column {self.value} not found in item {row}")
        return row[self.value]


RESERVED_KWS = ("SELECT", "FROM", "WHERE", "LIMIT")
STR_DELIMITERS = set(("'", '"'))

# Represents a parsed SQL statement.
ParsedOperation = NamedTuple(
    'ParsedOperation', [('op_type', str), ('cols', List[str]),
                        ('table_name', str), ('limit', int), ('expr', Node)])


def parse(sql: str) -> ParsedOperation:
    """
    Parse a string representing a valid SQL statement and return the
    corresponding ParsedOperation.
    """
    table_name = None
    cols = None
    op_type = None
    expr = None
    limit = float('inf')
    query_len = len(sql)
    state = "START"
    idx = 0

    while idx < query_len:
        char = sql[idx]
        # ignore spaces
        if char.isspace():
            idx += 1
        # parse next available operation, if any
        elif state == "START" or state == "NEXT_OP":
            if char.isalpha():
                token, idx = extract_op(sql, idx)
                if state == "START":
                    op_type = token
                    logging.debug(f"Reading {op_type} statement..")
                state = token
            else:
                raise ValueError("Invalid SQL statement!")
        # parse column names for SELECT
        elif state == "SELECT":
            if char.isalnum() or char == '*':
                cols, idx = extract_cols(sql, idx)
                state = "NEXT_OP"
            else:
                raise ValueError(
                    "Invalid SELECT statement! Column names cannot start with special characters.")
        # parse table name
        elif state == "FROM":
            if char.isalnum():
                table_name, idx = extract_table_name(sql, idx)
                logging.debug(
                    f"Selecting columns: {', '.join(cols)} from table: {table_name}")
                state = "NEXT_OP"
            else:
                raise ValueError(
                    "Invalid table name! Cannot start with special characters.")
        # parse filter expression
        elif state == "WHERE":
            expr, idx = extract_expr(sql, idx)
            state = "NEXT_OP"
        # parse limit value
        elif state == "LIMIT":
            limit, idx = extract_num(sql, idx)
            logging.debug(f"LIMIT to {limit} rows...")
            state = "END"
        elif state == "END":
            logging.debug("Parsing expression complete..")
            break
        else:
            raise ValueError(f"Invalid operation {state}")
    operation = None
    if op_type == "SELECT":
        operation = ParsedOperation(op_type, cols, table_name, limit, expr)
    else:
        raise ValueError(f"Invalid operation {op_type}")

    return operation


def execute(data: List[dict], operation: ParsedOperation) -> List:
    """
    Execute the parsed operation against the list of data objects.
    """

    results = []
    count = 0
    for item in data:
        if count >= operation.limit:
            break
        include = operation.expr.evaluate(item) if operation.expr else True
        if include:
            result_item = dict()
            if len(operation.cols) == 1 and operation.cols[0] == "*":
                result_item = item
            else:
                for col in operation.cols:
                    if col not in item:
                        raise ValueError(
                            f"Column {col} not found in table {operation.table_name}")
                    result_item[col] = item[col]
            results.append(result_item)
            count += 1

    return results


def extract_op(query: str, idx: int) -> Tuple[str, int]:
    """
    Extract keywords representing valid operations containing a-z characters.
    No special characters allowed in keywords.
    """
    token = ''
    i = idx
    while i < len(query) and query[i].isalpha():
        token += query[i]
        i += 1

    return token.upper(), i


def extract_col_from_expr(query: str, idx: int) -> Tuple[str, int]:
    """
    Extract first column name from filter condition expression start at idx.
    Column names must be alphanumeric chars or '_'.
    """
    token = ''
    i = idx
    while i < len(query) and (query[i].isalnum() or query[i] == '_'):
        token += query[i]
        i += 1

    return token, i


def extract_num(query: str, idx: int) -> Tuple[float, int]:
    """
    Extract first numeric type starting at idx as an int or float value.
    """
    token = ''
    i = idx
    isFloat = False
    while i < len(query) and (query[i].isnumeric() or query[i] == '.'):
        if query[i].isnumeric():
            token += query[i]
        elif query[i] == '.':
            if isFloat:
                raise ValueError("Invalid float!")
            isFloat = True
            token += query[i]
        i += 1
    if isFloat:
        return float(token), i
    return int(token), i


def extract_cols(query: str, idx: int) -> Tuple[List[str], int]:
    """
    Extracts comma-separated column names starting at idx.
    Spaces between col names are not allowed. Column names cannot contain
    special characters except underscore.
    """
    cols = list()
    i = idx
    cols_str = ""
    while i < len(query) and query[i].isspace() is False:
        cols_str += query[i]
        i += 1
    if cols_str != "*":
        cols = [x.strip() for x in cols_str.split(",") if x.strip()]
    else:
        cols.append(cols_str)
    return cols, i


def extract_table_name(query: str, idx: int) -> Tuple[str, int]:
    t_name = ""
    i = idx
    while i < len(query) and query[i].isspace() is False:
        t_name += query[i]
        i += 1
    return t_name, i


def extract_string_literal(query: str, idx: int) -> Tuple[str, int]:
    """
    Extract string value enclosed in quotes.
    """
    str_literal = ""
    i = idx + 1
    while i < len(query) and query[i] not in STR_DELIMITERS:
        str_literal += query[i]
        i += 1
    return str_literal, i + 1


def get_next_expr_token(query: str, idx: int) -> Tuple[List[Any], int]:
    """
    Extract the next token in the WHERE clause expression starting at idx.
    """

    i = idx
    while i < len(query):
        char = query[i]
        # ignore spaces between tokens
        if char.isspace():
            i += 1
        # extract numeric types
        elif char.isnumeric():
            return extract_num(query, i)
        # tokenize parentheses
        elif char == '(':
            return char, i + 1
        elif char == ")":
            return char, i + 1
            i += 1
        # extract string literals
        elif char in STR_DELIMITERS:
            return extract_string_literal(query, i)
        # should be an operator/column name/next token
        else:
            # check for subsequent keywords (expression complete)
            for kw in RESERVED_KWS:
                if query.upper().startswith(kw, i):
                    return None, i
            # check operators
            for op in OPS.keys():
                if query.upper().startswith(op, i):
                    return op, i + len(op)
            # has to be a column name
            return extract_col_from_expr(query, i)

    return None, i


def extract_expr(query: str, i: int) -> Tuple[Node, int]:
    """
    Parse WHERE clause expression as a tree and return the head.
    """

    stack = list()
    operators = list()
    curr_token, i = get_next_expr_token(query, i)
    while curr_token:
        if isinstance(curr_token, str) and curr_token.upper() in OPS:
            if operators and operators[-1] != '(' and \
                    OP_PRECEDENCE[curr_token.upper()] < OP_PRECEDENCE[operators[-1]]:
                right = stack.pop(-1)
                left = stack.pop(-1)
                op = operators.pop(-1)
                # if the left operand is not an operator, it must be a column name
                if isinstance(left, Literal):
                    left = ColName(left.value)
                logging.debug(
                    f"Binary operator: {op} with op1 = {left.value} and op2 = {right.value}")
                stack.append(BinaryOperator(op, left, right))
            operators.append(curr_token.upper())
        elif curr_token == "(":
            operators.append(curr_token)
        elif curr_token == ")":
            # Evaluate everything inside parentheses
            while operators and operators[-1] != '(':
                right = stack.pop(-1)
                left = stack.pop(-1)
                op = operators.pop(-1)
                # if the left operand is not an operator, it must be a column name
                if isinstance(left, Literal):
                    left = ColName(left.value)
                logging.debug(
                    f"Binary operator: {op} with op1 = {left.value} and op2 = {right.value}")
                stack.append(BinaryOperator(op, left, right))
            # Remove trailing '('
            if operators:
                operators.pop(-1)
        else:
            stack.append(Literal(curr_token))
        curr_token, i = get_next_expr_token(query, i)

    # Evaluate remaining ops
    while operators:
        right = stack.pop(-1)
        left = stack.pop(-1)
        if isinstance(left, Literal):
            left = ColName(left.value)
        operator = operators.pop(-1)
        logging.debug(
            f"Binary operator: {operator} with op1 = {left.value} and op2 = {right.value}")
        stack.append(BinaryOperator(operator, left, right))

    if stack:
        return stack[0], i
    return None, i
