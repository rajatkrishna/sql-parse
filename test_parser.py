import unittest
import logging
import parser
import executor


logging.getLogger().setLevel(logging.DEBUG)


class TestParser(unittest.TestCase):
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

    def test_simple_select_all_with_cond(self):
        sql = "SELECT * FROM table WHERE row=1024"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(len(res.filters) == 3)
        item = {"row": 1024, "rowb": "text", "abc": "quantity"}
        result = executor.eval_filters(item, res)
        self.assertTrue(result)

    def test_and_condition(self):
        sql = "SELECT row,rowb FROM table WHERE row=1024 AND rowb='text'"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(len(res.filters) == 7)
        item = {"row": 1024, "rowb": "text", "abc": "quantity"}
        result = executor.eval_filters(item, res)
        self.assertTrue(result)

    def test_or_condition(self):
        sql = "SELECT row,rowb FROM table WHERE row=1024 OR rowb='text'"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(len(res.filters) == 7)
        item = {"row": 1024, "rowb": "text22", "abc": "quantity"}
        result = executor.eval_filters(item, res)
        self.assertTrue(result)

    def test_multi_cond1(self):
        sql = "SELECT row,rowb FROM table WHERE row < 2000 AND ((rowb = text22) OR abc='quality')"
        res = parser.parse(sql)
        self.assertTrue(res.table_name == "table")
        self.assertTrue(len(res.filters) == 15)
        item = {"row": 1024, "rowb": "text22", "abc": "quantity"}
        result = executor.eval_filters(item, res)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
