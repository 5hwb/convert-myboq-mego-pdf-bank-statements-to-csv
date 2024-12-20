import argparse
from datetime import datetime
import re
from file_io import load_file_to_str, save_str_to_file

CSV_HEADER = 'Date,Processed,Description,Debits ($),Credits ($),Balance ($)'
REGEX_DATE = r'([0-9]{2}-[A-Z][a-z]{2})'
REGEX_DESCRIPTION = r'(.+?)'
REGEX_AMOUNT = r'([0-9.,-]+)'
REGEX_TRANSACTION_WITHOUT_BALANCE = REGEX_DATE + r'\s+' + REGEX_DATE + r'\s{2,}' + REGEX_DESCRIPTION + r'\s{2,}' + REGEX_AMOUNT # This accounts for transactions where the balance is blank (e.g. when it reaches $0.00)
REGEX_TRANSACTION = REGEX_TRANSACTION_WITHOUT_BALANCE + r'\s+' + REGEX_AMOUNT
# Full regex: ([0-9]{2}-[A-Z][a-z]{2})\s+([0-9]{2}-[A-Z][a-z]{2})\s{2,}(.+)\s{2,}([0-9.,-]+)\s{2,}([0-9.,-]+)
# For matching just the dates: ([0-9]{2}-[A-Z][a-z]{2})\s+([0-9]{2}-[A-Z][a-z]{2})

REGEX_CLOSING_BALANCE = r'(Closing Balance)\s+' + REGEX_AMOUNT
REGEX_END_OF_PAGE = r'(Page|Statement continues over|Bank of Queensland|Please check your|Remember to retain|mebank|Account security tips|•)'

def change_to_ymd_date_format(date, year):
    if date == '':
        return date
    return datetime.strptime(date + ' ' + year, '%d %b %Y').strftime('%Y-%m-%d')

class Transaction:
    def __init__(self, date_received, date_processed, description, changes, balance, year):
        self.date_received = change_to_ymd_date_format(date_received.replace('-', ' '), year)
        self.date_processed = change_to_ymd_date_format(date_processed.replace('-', ' '), year)
        self.description = description.strip().replace(',', ' ')
        self.changes = changes.replace(',', '')
        self.balance = balance.replace(',', '')

    def __str__(self) -> str:
        return '{} {} - \"{}\": {} ({})'.format(self.date_received, self.date_processed, self.description, self.changes, self.balance)

def convert_input_into_transactions_list(file_to_load, current_year, is_debugging=False):
    input_data = load_file_to_str(file_to_load).split('\n')
    curr_transaction = None
    transactions_list = []

    for input_line in input_data:
        if len(input_line) == 0:
            continue

        is_closing_balance = re.search(REGEX_CLOSING_BALANCE, input_line) != None
        is_new_transaction = re.search(REGEX_TRANSACTION, input_line) != None
        is_new_transaction_without_balance = re.search(REGEX_TRANSACTION_WITHOUT_BALANCE, input_line) != None
        is_end_of_page = re.search(REGEX_END_OF_PAGE, input_line) != None
        is_reading_transaction = curr_transaction != None
        if is_debugging: print('[line] isNewTxn={} isEndOfPage={} isReadingTxn={} isNewTxnWithoutBalance={} isNewTxn={} "{}"'.format(is_new_transaction_without_balance, is_end_of_page, is_reading_transaction, is_new_transaction_without_balance, is_new_transaction, input_line))

        if is_closing_balance:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)
            parsed_input = re.search(REGEX_CLOSING_BALANCE, input_line).groups()
            curr_transaction = Transaction('', '', parsed_input[0], '0.00', parsed_input[1], current_year)
            if is_debugging: print('TRANSACTION: {}'.format(str(curr_transaction)))

        elif is_new_transaction_without_balance:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)
            transaction_regex = REGEX_TRANSACTION if is_new_transaction else REGEX_TRANSACTION_WITHOUT_BALANCE
            parsed_input = re.search(transaction_regex, input_line).groups()
            curr_transaction = Transaction(
                    parsed_input[0], parsed_input[1],
                    parsed_input[2], parsed_input[3],
                    parsed_input[4] if is_new_transaction else '0.00',
                    current_year
            )
            if is_debugging: print('TRANSACTION: {}'.format(str(curr_transaction)))

        elif is_reading_transaction:
            if is_end_of_page:
                transactions_list.append(curr_transaction)
                curr_transaction = None
                continue
            curr_transaction.description += ' ' + input_line.strip().replace(',', ' ')

        else:
            curr_transaction = None
            continue

    print('And the final result shall be:')
    [print(transaction) for transaction in transactions_list]
    print(len(transactions_list))

    return transactions_list
    
def generate_csv(transactions_list, file_to_save, is_reversed=False):
    file_to_save = file_to_save.replace('.txt', '.new.csv')
    output_data = CSV_HEADER + '\n'

    transactions_list = reversed(transactions_list) if is_reversed else transactions_list

    for transaction in transactions_list:
        change_is_debited = transaction.changes[0] == '-'
        csv_line = '{},{},{},{},,{}' if change_is_debited else '{},{},{},,{},{}'
        output_data += csv_line.format(transaction.date_received, transaction.date_processed, transaction.description, transaction.changes, transaction.balance) + '\n'

    save_str_to_file(file_to_save, output_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='ConvertBankStatementPDFTextExportToCSV',
            description='This script aims to extract the desired transaction data from the Okular exported text file and convert it into a CSV format.')
    parser.add_argument('-f', '--filename', required=True, help='Filename of the text file to convert to CSV')
    parser.add_argument('-y', '--current-year', required=True, help='The current year to add to the transaction date')
    parser.add_argument('-r', '--reverse', action='store_true', help='If provided, reverse the output')
    parser.add_argument('-d', '--debug', action='store_true', help='If provided, enable transaction debugging output')

    args = parser.parse_args()
    print(args)

    transactions_list = convert_input_into_transactions_list(args.filename, args.current_year, args.debug)
    generate_csv(transactions_list, args.filename, args.reverse)
