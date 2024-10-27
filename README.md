# Script to convert PDF bank statement text data into CSV

Some banks are only able to export bank transactions in PDF form via the statements, as they do not have a CSV export option. This poses issues when I want to copy this data over into my spreadsheets for finance accounting purposes, as I previously would've needed to manually transcribe each transaction one by one.

There is a Linux program called `pdftotext` which can export the contents of the PDF to a text file, which is well structured. But as the transaction description may be spread out over multiple lines, using regex to convert it to a CSV isn't possible.

This script aims to extract the desired transaction data from the exported PDF text file and convert it into a CSV format which can then be copied to a spreadsheet.

**Before: Raw exported PDF transaction data**

```
                                                  SaveU statement.
                                                  Statement period
                                                  01 Jul 24 - 31 Aug 24

                       Ghuji Kolp
                       000 SOME ST
                       NICEVILLE NSW 0000

                                                  Account summary.
      Account name     SaveU                    Opening balance         0

      Account BSB      ###-###
                                                  Total credits      555.00

      Account number   #########
                                                  Total debits       -542.00

                                                  Closing balance    11.00

Transactions
Date     Processed   Description       Debits ($)   Credits ($)   Balance ($)

09-Sep   09-Sep      From: Jonny Nau                5.00          5.00
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
                Account security tips.

   Foolproof ways to enhance account security.
   Disco 101 – making your money DANCE.
```

**After: Perfectly formatted and aligned transactions CSV file without all the extra fluff**

```csv
Date,Processed,Description,Debits ($),Credits ($),Balance ($)
2024-09-09,2024-09-09,From: Jonny Nau this is a sample test,,5.00,5.00
2024-09-09,2024-09-09,To: Acc 0######,-3.00,,2.00
2024-09-15,2024-09-15,From: SALARY NICESTARTUP this is just a test,,50.00,52.00
2024-09-15,2024-09-15,To: Acc 0######,-52.00,,0.00
2024-09-17,2024-09-17,From: SALARY NICESTARTUP salary-sept,,500.00,500.00
2024-09-17,2024-09-17,To: Acc 0######,-489.00,,11.00
,,Closing Balance,,0.00,11.00
```

## Usage example

```sh
pdftotext -layout bank-statement.pdf | python3 convert_pdf_statement_text_to_csv.py -i bank-statement.txt -o bank-statement.csv -y 2024
```
