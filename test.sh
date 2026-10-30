#!/bin/env bash

run_test(){
  echo -n "Test '$1' "
  ($1 >/dev/null 2>&1) && (
    echo -e "\x1b[32mPASSED\x1b[0m"
  ) || (
    echo -e "\x1b[31mFAILED\x1b[0m"
  )
}

run_test "pyright firepipe"
run_test "python tests/test_lexer.py"
run_test "python tests/test_parser.py"
run_test "python tests/test_processor.py"
