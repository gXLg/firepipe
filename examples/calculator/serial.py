import pickle
from os.path import exists

from cli import run_cli

if __name__ == "__main__":
  if not exists("calc.pkl"):
    from base import create_calculator
    calc = create_calculator()
  else:
    with open("calc.pkl", "rb") as cfile:
      calc = pickle.load(cfile)

  run_cli(calc)

  with open("calc.pkl", "wb") as cfile:
    pickle.dump(calc, cfile)
