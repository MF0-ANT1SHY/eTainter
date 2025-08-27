#!/usr/bin/env python3
import csv
import os
import sys


def usage():
    print(f"Usage: {os.path.basename(sys.argv[0])} <dir> [--all]", file=sys.stderr)
    print("  <dir>   Root directory containing <contract_address>/log.txt", file=sys.stderr)
    print("  --all   Print all addresses with a 1/0 match flag instead of only matches", file=sys.stderr)

def is_probable_address(name: str) -> bool:
    # Relaxed heuristic: 0x + 40 hex chars (Ethereum-style). Adjust if needed.
    if len(name) != 42:
        return False
    if not name.startswith("0x"):
        return False
    hexpart = name[2:]
    return all(c in "0123456789abcdefABCDEF" for c in hexpart)

def scan_dir(root: str, print_all: bool = False):
    # Prepare CSV writer to stdout
    writer = csv.writer(sys.stdout, lineterminator="\n")
    # Optional header (comment out if not desired)
    # writer.writerow(["contract_address", "matched"])
    try:
        entries = os.listdir(root)
    except OSError as e:
        print(f"Error: cannot list directory '{root}': {e}", file=sys.stderr)
        sys.exit(2)

    for name in sorted(entries):
        subpath = os.path.join(root, name)
        if not os.path.isdir(subpath):
            continue

        # If you want to require address format, uncomment this check:
        # if not is_probable_address(name):
        #     continue

        log_path = os.path.join(subpath, "log.txt")
        if not os.path.isfile(log_path):
            if print_all:
                writer.writerow([name, 0])
            continue

        matched = 0
        try:
            # Read efficiently and stop early on match
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "in function" in line:
                        matched = 1
                        break
        except OSError as e:
            # If unreadable, treat as no match unless you want to report errors
            if print_all:
                writer.writerow([name, 0])
            continue

        if matched or print_all:
            # Print CSV: contract_address, matched_flag
            writer.writerow([name, matched])

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
        sys.exit(1)

    root = sys.argv[1]
    print_all = False
    if len(sys.argv) == 3:
        if sys.argv[2] == "--all":
            print_all = True
        else:
            usage()
            sys.exit(1)

    if not os.path.isdir(root):
        print(f"Error: '{root}' is not a directory", file=sys.stderr)
        sys.exit(2)

    scan_dir(root, print_all)

if __name__ == "__main__":
    main()