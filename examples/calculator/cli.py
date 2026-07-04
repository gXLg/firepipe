from firepipe.utils import FirepipeError

def run_cli(calc):
  print("Simple Integer Calculator")
  while True:
    try:
      expr = input("> ")
    except EOFError: break
    except KeyboardInterrupt: break
    if not expr: break
    try:
      print(calc.work(expr))
    except FirepipeError as err:
      print(err)
    print()
  print("Bye!")

if __name__ == "__main__":
  from base import create_calculator
  run_cli(create_calculator())
