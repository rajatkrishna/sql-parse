import unittest
import logging
import parser


logging.getLogger().setLevel(logging.DEBUG)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.item = {"row1": 1024, "row2": "text", "row3":99.999, "row_4": "*@#&!(@*#&"}

    def test_simple_select_all(self):
        sql = "SELECT * FROM table"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(len(res.cols) == 1 and res.cols[0] == "*")

    def test_simple_select_single_row(self):
        sql = "SELECT row FROM table"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(len(res.cols) == 1 and res.cols[0] == "row")

    def test_simple_select_multi_rows(self):
        sql = "SELECT rowa,rowb FROM table"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(len(res.cols) == 2)

    def test_and_condition(self):
        sql = "SELECT row1,row2 FROM table WHERE row1=1024 AND row2='text'"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(res.expr.evaluate(self.item))

    def test_or_condition(self):
        sql = "SELECT row1,row2 FROM table WHERE row1=1024 OR row2='text'"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(res.expr.evaluate(self.item))

    def test_multi_cond1(self):
        sql = "SELECT row1,row2 FROM table WHERE row1 < 2000 AND ((row2 = text22) OR row_4='*@#&!(@*#&')"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(res.expr.evaluate(self.item))

    def test_invalid_num(self):
        sql = "SELECT row1,row2 FROM table WHERE row3=99.99.99"
        res = None
        try:
            res = parser.parse(sql)
        except ValueError:
            return
        self.fail(res)

    def test_valid_float(self):
        sql = "SELECT row1,row2 FROM table WHERE row3=99.999"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(res.expr.evaluate(self.item))

    def test_valid_int(self):
        sql = "SELECT * FROM table WHERE row1=1024"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        result = res.expr.evaluate(self.item)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
