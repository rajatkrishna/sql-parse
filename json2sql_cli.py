import argparse
import json
import parser
import executor
import time


def load_json(path: str) -> list:
    with open(path, 'r') as file:
        data = json.load(file)
    return data


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("data_path", type=str,
                            help="Path to json containing data.")

    args = arg_parser.parse_args()
    data_path = args.data_path.strip()

    data = load_json(data_path)
    print(f"Table of size {len(data)} created.")

    while True:
        sql_str = input("Enter the SQL query or 0 to exit:\n")
        if sql_str == "0":
            print("Goodbye!")
            exit(0)
        op = None
        try:
            start = time.time()
            op = parser.parse(sql_str)
            print(f"Query parsed in {time.time() - start:.3f} seconds...")
        except Exception as e:
            print(f"Failed to parse query: {e}")

        if op:
            try:
                start = time.time()
                results = executor.execute(data, op)
                print(
                    f"Query executed in {time.time() - start:.3f} seconds...")
                print(results)
            except Exception as e:
                print(f"Failed to execute query: {e}")
