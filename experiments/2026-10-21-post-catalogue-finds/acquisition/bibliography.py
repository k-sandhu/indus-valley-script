"""Check bibliographic fields without exporting source passages."""
import argparse
import importlib.util
import pathlib
import sys

sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser()
    for name in ("root", "raw", "records"):
        parser.add_argument("--" + name, type=pathlib.Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("bibliography_fields", args.records.resolve() / "bibliography_fields.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.repair(args)


if __name__ == "__main__":
    main()
