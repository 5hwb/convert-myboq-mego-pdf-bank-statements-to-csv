# MyBOQ / ME Go bank statement PDF to CSV script

This is a pipeline for converting MyBOQ and ME Go bank statement PDF files into a CSV format for easier finance accounting. It does the following:

1. Convert the PDF file using the `pdftotext` tool into to a structured text file
2. Extract transaction data from the text file with a custom Python script and convert it into a CSV format which can then be copied to a spreadsheet for further reference.

**Before: Raw exported PDF transaction data**

```
                                                  SaveOne statement.
                                                  Statement period
                                                  01 Jul 24 - 30 Sep 24

                       Huji Kolp
                       000 SOME ST
                       NICEVILLE NSC 0000

                                                  Account summary.
      Account name     SaveOne                    Opening balance         0

      Account BSB      ###-###
                                                  Total credits      555.00

      Account number   #########
                                                  Total debits       -542.00

                                                  Closing balance    11.00

Transactions
Date     Processed   Description       Debits ($)   Credits ($)   Balance ($)

09-Sep   09-Sep      From: Jonny N                  5.00          5.00
                     this is a
                     sample test
09-Sep   09-Sep      To: Acc 0######   -3.00                      2.00
15-Sep   15-Sep      From: SALARY                   50.00         52.00
                     NICESTARTUP
                     this is just a
                     test
15-Sep   15-Sep      To: Acc 0######   -52.00
17-Sep   17-Sep      From: SALARY                   500.00        500.00
                     NICESTARTUP
                     salary-sept
17-Sep   17-Sep      To: Acc 0######   -489.00                    11.00
                     Closing Balance                              11.00
Page 1 of 2 | Statement continues over
                Account security tips

   Foolproof ways to enhance account security
   Disco 101 – making your money DANCE.
```

**After: Perfectly formatted and aligned transactions CSV file without all the extra fluff**

```csv
Date,Processed,Description,Debits ($),Credits ($),Balance ($)
2024-09-09,2024-09-09,From: Jonny N this is a sample test,,5.00,5.00
2024-09-09,2024-09-09,To: Acc 0######,-3.00,,2.00
2024-09-15,2024-09-15,From: SALARY NICESTARTUP this is just a test,,50.00,52.00
2024-09-15,2024-09-15,To: Acc 0######,-52.00,,0.00
2024-09-17,2024-09-17,From: SALARY NICESTARTUP salary-sept,,500.00,500.00
2024-09-17,2024-09-17,To: Acc 0######,-489.00,,11.00
,,Closing Balance,,0.00,11.00
```

## Usage

Execute the convert_pdf_statement_to_csv.sh Bash script in a terminal. Change 'example-bank-statement.pdf' into the name of the bank statement file to convert, and 2024 to the year the statement was introduced.

```sh
./convert_pdf_statement_to_csv.sh -f 'example-bank-statement.pdf' -y 2024
```

Before running the script for the 1st time, mark it as executable first using `chmod +x convert_pdf_statement_to_csv.sh`.

### Optional flags

- `-r`, `--reverse`: Order the transactions list by their dates in descending order.
- `-l`, `--legacy`: Process the bank statement using ME Go's pre-2024 transaction format of (debit) (credit) (balance) instead of (debit or credit) (balance), and a date format of 1 Jan instead of 01-Jan.
- `-d`, `--debug`: Toggle transaction debugging output.

e.g. to debug, use

```sh
./convert_pdf_statement_to_csv.sh -f 'bank-statement.pdf' -y 2024 -d
```

### Testing

This repo comes with a sample PDF statement text file which can be used to test the Python script.

```sh
python3 convert_pdf_statement_text_to_csv.py -f "example-pdf-statement.txt" -y 2024 -d
```
