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
ParsedOperation = NamedTuple(
    'ParsedOperation', [('op_type', str), ('cols', List[str]), ('table_name', str), ('limit', int), ('filters', List[Any])])
STR_DELIMITERS = set(("'", '"'))


def parse(sql: str) -> ParsedOperation:
    """
    Parse a string representing a valid SQL statement and return the
    corresponding ParsedOperation.
    """
    table_name = None
    cols = None
    op_type = None
    filter = []
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
            filter, idx = tokenize_cond_expr(sql, idx)
            logging.debug(f"Tokenized WHERE clause: {filter}")
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
        operation = ParsedOperation(op_type, cols, table_name, limit, filter)
    else:
        raise ValueError(f"Invalid operation {op_type}")

    return operation


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
    Extract first decimal starting at idx as a float value.
    """
    token = ''
    i = idx
    while i < len(query) and (query[i].isnumeric() or query[i] == '.'):
        token += query[i]
        i += 1
    return float(token), i


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
    i = idx
    while i < len(query) and query[i] not in STR_DELIMITERS:
        str_literal += query[i]
        i += 1
    return str_literal, i + 1


def tokenize_cond_expr(query: str, idx: int) -> Tuple[List[Any], int]:
    tokens = []
    i = idx
    token = ""
    while i < len(query):
        char = query[i]
        # ignore spaces between tokens
        if char.isspace():
            i += 1
        # extract numeric types
        elif char.isnumeric():
            token, i = extract_num(query, i)
            tokens.append(token)
        # tokenize parentheses
        elif char == '(':
            tokens.append(char)
            i += 1
        elif char == ")":
            tokens.append(char)
            i += 1
        # extract string literals
        elif char in STR_DELIMITERS:
            token, i = extract_string_literal(query, i)
        # should be an operator or column name
        else:
            if query.startswith("LIMIT", i):
                return tokens, i
            if char.isalpha():  # either a column name or a string-operator
                token, i = extract_col_from_expr(query, i)
                tokens.append(token)
            else:
                for op in OPS.keys():  # compare against known operators
                    if query.startswith(op, i):
                        tokens.append(op)
                        i += len(op)

    return tokens, i
