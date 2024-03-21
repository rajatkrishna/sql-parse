from typing import Any
import logging
import parser


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
        return parser.OPS[self.value](l_result, r_result)


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
