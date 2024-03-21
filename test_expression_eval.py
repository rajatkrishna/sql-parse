import unittest
import logging
import parser


logging.getLogger().setLevel(logging.DEBUG)


class TestExpressionEval(unittest.TestCase):
    def setUp(self):
        self.item = {"row1": 1024, "row2": "text",
                     "row3": 99.999, "row_4": "*@#&!(@*#&"}

    def test_multi_cond1(self):
        expr = "row1 < 2000 AND ((row2 = text22) OR row_4='*@#&!(@*#&')"
        astree, _ = parser.extract_expr(expr, 0)
        self.assertTrue(astree.evaluate(self.item))

    def test_multi_cond2(self):
        expr = "row1 < 2000 AND ((row2 = text22) OR row_4='@*#&')"
        astree, _ = parser.extract_expr(expr, 0)
        self.assertFalse(astree.evaluate(self.item))

    def test_multi_cond3(self):
        expr = "(row2 != text) OR row3<99.9999 AND (row_4='*#*#*' or row1=1024)"
        astree, _ = parser.extract_expr(expr, 0)
        self.assertTrue(astree.evaluate(self.item))

    def test_multi_cond4(self):
        expr = "(row2 != text) OR row3<96.8999 AND (row_4='*#*#*' or row1=1024)"
        astree, _ = parser.extract_expr(expr, 0)
        self.assertFalse(astree.evaluate(self.item))


if __name__ == '__main__':
    unittest.main()
