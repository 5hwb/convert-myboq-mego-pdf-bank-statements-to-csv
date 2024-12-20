#!/usr/bin/env bash
filename=${1/.pdf/}
year=$2
pdftotext -layout "$filename.pdf"
python3 convert_pdf_statement_text_to_csv.py -r -f "$filename.txt" -y $year