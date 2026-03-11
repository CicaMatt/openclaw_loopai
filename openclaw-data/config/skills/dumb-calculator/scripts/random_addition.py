#!/usr/bin/env python3
import json
import random


def main():
    a = random.randint(0, 999)
    b = random.randint(0, 999)
    result = a + b

    payload = {
        "expression": f"{a} + {b}",
        "result": result
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
