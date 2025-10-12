import pandas as pd
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_excel.py <input_file.txt|input_file.csv>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)

    # Generate output Excel filename
    output_file = os.path.splitext(input_file)[0] + ".xlsx"

    try:
        # Read file based on extension
        if input_file.endswith(".txt"):
            df = pd.read_csv(input_file, sep='\t')
        elif input_file.endswith(".csv"):
            df = pd.read_csv(input_file)
        else:
            print("Unsupported file format. Only .txt and .csv are supported.")
            sys.exit(1)
    except FileNotFoundError:
        print("The file was not found. Please check the path.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print("The file is empty.")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"Parsing error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error while reading file: {e}")
        sys.exit(1)

    try:
        df.to_excel(output_file, index=False)
        print(f"Excel file created: {output_file}")
    except PermissionError:
        print("Permission denied. Make sure the file is not open and you have write access.")
        sys.exit(1)
    except Exception as e:
        print(f"Error writing Excel file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
