#!/bin/bash

echo -e "\nrunning tests/user_test.py"
python3 -m pytest -s -q tests/user_test.py

echo -e "\nrunning tests/transaction_test.py"
python3 -m pytest -s -q tests/transaction_test.py
