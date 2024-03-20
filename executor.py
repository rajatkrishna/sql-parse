import parser
import logging
from typing import List


def eval_filters(row: dict, operation: parser.ParsedOperation) -> bool:
    """
    Evaluate row against operation's filter conditions.
    Returns boolean representing eval result.
    """
    operators = list()
    operands = list()

    length = len(operation.filters)
    idx = 0
    while idx < length:
        curr_token = operation.filters[idx]
        if curr_token in parser.OPS:
            # if current operator has greater precedence than last in the stack, pop and evaluate op
            if operators and operators[-1] != '(' and parser.OP_PRECEDENCE[curr_token] < parser.OP_PRECEDENCE[operators[-1]]:
                op2 = operands.pop(-1)
                op1 = operands.pop(-1)
                # op1 should be either column name or previously evaluated result
                if not isinstance(op1, bool):
                    if op1 not in row:
                        raise ValueError(
                            f"Column {op1} not found in table {operation.table_name}")
                    op1 = row[op1]
                operator = operators.pop(-1)
                logging.debug(
                    f"Executing operation: {op1} {operator} {op2}")
                operands.append(parser.OPS[operator](op1, op2))
            operators.append(curr_token)
        elif curr_token == "(":
            operators.append(curr_token)
        elif curr_token == ")":
            # Evaluate everything inside parentheses
            operator = operators.pop(-1)
            while operator != "(":
                op2 = operands.pop(-1)
                op1 = operands.pop(-1)
                if not isinstance(op1, bool):
                    if op1 not in row:
                        raise ValueError(
                            f"Column {op1} not found in table {operation.table_name}")
                    op1 = row[op1]
                logging.debug(
                    f"Executing operation: {op1} {operator} {op2}")
                operands.append(parser.OPS[operator](op1, op2))
                operator = operators.pop(-1)
        else:
            operands.append(curr_token)
        idx += 1

    # Evaluate remaining ops
    while operators:
        op2 = operands.pop(-1)
        op1 = operands.pop(-1)
        if not isinstance(op1, bool):
            if op1 not in row:
                raise ValueError(
                    f"Column {op1} not found in table {operation.table_name}")
            op1 = row[op1]
        operator = operators.pop(-1)
        logging.debug(f"Executing operation: {op1} {operator} {op2}")
        operands.append(parser.OPS[operator](op1, op2))

    resp = True
    while operands:
        op = operands.pop(-1)
        if not isinstance(op, bool):
            raise ValueError("Invalid WHERE clause!")
        resp = resp and op
    return resp


def execute(data: list, operation: parser.ParsedOperation) -> List:
    results = []
    count = 0
    for item in data:
        if count >= operation.limit:
            break
        if eval_filters(item, operation):
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
