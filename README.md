## Simple Python SQL Parser

### Setup

- Install dependencies
```
pip install -r requirements.txt
```

### Usage

To run from the command line,
```
python3 json2sql_cli.py <path-to-json>
```

Example:

```
rajat@MacBook-Pro % python3 json2sql_cli.py data.json
Table of size 2 created.
Enter the SQL query or 0 to exit:
select * from table where state='California'
Query parsed in 0.001 seconds...
Query executed in 0.000 seconds...
state       region           pop    pop_male    pop_female
----------  --------  ----------  ----------  ------------
California  West      2312312321     3123123        123123
```
