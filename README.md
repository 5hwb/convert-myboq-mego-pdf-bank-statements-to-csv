# Script to convert PDF bank statement exports from Okular PDF reader into CSV

Some banks are only able to export bank transactions in PDF form via the statements, as they do not have a CSV export option. This poses issues when I want to copy this data over into my spreadsheets for finance accounting purposes, as I'll need to manually transcribe each transaction one by one.

Recently, I found that the Okular PDF reader in Linux can export the contents to a text file which is reasonably structured. But as the transaction description may be spread out over multiple lines, using regex will not be possible.

This script aims to extract the desired transaction data from the Okular exported text file and convert it into a CSV format.
