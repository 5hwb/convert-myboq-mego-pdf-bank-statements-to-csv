#!/usr/bin/env bash

# Process the arguments - originally from https://stackoverflow.com/a/33826763
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -f|--filename) filename=${2/.pdf/}; shift ;;
        -y|--year) year=$2; shift ;;
        -l|--legacy) legacy_flag=-l ;;
        -d|--debug) debugging_flag=-d ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "Filename: $filename"
echo "Year: $year"
echo "Legacy?: $legacy_flag"
echo "Debug?: $debugging_flag"

# Main pipeline
pdftotext -layout "$filename.pdf"
python3 convert_pdf_statement_text_to_csv.py -r -f "$filename.txt" -y $year $legacy_flag $debugging_flag

# Delete the intermediary txt file if not debugging
if [[ ! "$debugging_flag" ]]; then
  echo "Will delete"
  rm "$filename.txt"
fi

# ./convert_pdf_statement_to_csv.sh -f 'bank-statement.pdf' -y 2024 -d