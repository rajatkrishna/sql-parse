import parser
from typing import List


def execute(data: list, operation: parser.ParsedOperation) -> List:
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
