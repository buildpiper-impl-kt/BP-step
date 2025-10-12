import pandas as pd
import os
import sys
import re

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def clean_ascii_table(file_path):
    """Parse ASCII table with | borders"""
    rows = []
    headers = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            # Skip border lines
            if re.match(r'^\+[-+]+$', line):
                continue
            if not line.strip():
                continue
            # Split by | and strip spaces
            parts = [p.strip() for p in line.strip('|').split('|')]
            if not headers:
                headers = parts
            else:
                if len(parts) == len(headers):
                    rows.append(parts)
                else:
                    print(f"{YELLOW}WARNING: Skipping malformed line:{RESET} {line}")
    return headers, rows

def detect_and_read(file_path):
    """Detect file type and separator, return pandas DataFrame"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext == ".txt":
        with open(file_path, 'r') as f:
            # Skip empty lines and border lines to find the first meaningful line
            first_line = ""
            for line in f:
                line = line.strip()
                if line and not line.startswith('+'):
                    first_line = line
                    break

            # ASCII table if first meaningful line starts with |
            if first_line.startswith('|') and '|' in first_line:
                headers, rows = clean_ascii_table(file_path)
                if not rows:
                    raise ValueError("No data found in ASCII table")
                return pd.DataFrame(rows, columns=headers)
            # Tab-separated
            elif '\t' in first_line:
                return pd.read_csv(file_path, sep='\t')
            # Comma-separated
            elif ',' in first_line:
                return pd.read_csv(file_path)
            else:
                raise ValueError("TXT file separator not recognized (tab, comma, or ASCII table expected)")
    else:
        raise ValueError("Unsupported file format. Only .csv and .txt are supported.")

def main():
    input_file = os.getenv("INPUT_FILE")
    if not input_file:
        print(f"{RED}ERROR:{RESET} Environment variable INPUT_FILE not set.")
        sys.exit(1)

    input_file = os.path.abspath(input_file)
    if not os.path.isfile(input_file):
        print(f"{RED}ERROR:{RESET} File not found: {input_file}")
        sys.exit(1)

    output_file = os.path.splitext(input_file)[0] + ".xlsx"

    try:
        print(f"{YELLOW}INFO: Detecting file type and reading data...{RESET}")
        df = detect_and_read(input_file)
        df.to_excel(output_file, index=False)
        print(f"{GREEN}SUCCESS:{RESET} Excel file created: {output_file}")
        print(f"{YELLOW}INFO: {df.shape[0]} rows and {df.shape[1]} columns converted.{RESET}")

    except pd.errors.EmptyDataError:
        print(f"{YELLOW}WARNING: The file is empty.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}ERROR:{RESET} {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
