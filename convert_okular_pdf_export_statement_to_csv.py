import argparse
import re
from file_io import load_file_to_str, save_str_to_file

CSV_HEADER = 'Date,Processed,Description,Debits ($),Credits ($),Balance ($)'
REGEX_DATE = r'([0-9]{2}-[A-Z][a-z]{2})'
REGEX_DESCRIPTION = r'(.+?)'
REGEX_AMOUNT = r'([0-9.,-]+)'
REGEX_TRANSACTION = REGEX_DATE + r'\s+' + REGEX_DATE + r'\s{2,}' + REGEX_DESCRIPTION + r'\s{2,}' + REGEX_AMOUNT
REGEX_TRANSACTION_WITH_BALANCE = REGEX_TRANSACTION + r'\s+' + REGEX_AMOUNT
# Full regex: ([0-9]{2}-[A-Z][a-z]{2})\s+([0-9]{2}-[A-Z][a-z]{2})\s{2,}(.+)\s{2,}([0-9.,-]+)\s{2,}([0-9.,-]+)
# For matching just the dates: ([0-9]{2}-[A-Z][a-z]{2})\s+([0-9]{2}-[A-Z][a-z]{2})

REGEX_CLOSING_BALANCE = r'(Closing Balance)\s+' + REGEX_AMOUNT
REGEX_END_OF_PAGE = r'(Page|Statement continues over|Bank of Queensland|Please check your|Remember to retain|mebank|Account security tips|•)'

class Transaction:
    def __init__(self, date_received, date_processed, description, changes, balance):
        self.date_received = date_received.replace('-', ' ')   # TODO: format this into a full date
        self.date_processed = date_processed.replace('-', ' ') # TODO: format this into a full date
        self.description = description.strip().replace(',', ' ')
        self.changes = changes.replace(',', '')
        self.balance = balance.replace(',', '')

    def __str__(self) -> str:
        return '{} {} - \"{}\": {} ({})'.format(self.date_received, self.date_processed, self.description, self.changes, self.balance)

def convert_input_into_transactions_list(file_to_load):
    input_data = load_file_to_str(file_to_load).split('\n')
    curr_transaction = None
    transactions_list = []

    for input_line in input_data:
        is_closing_balance = re.search(REGEX_CLOSING_BALANCE, input_line) != None
        is_new_transaction_with_balance = re.search(REGEX_TRANSACTION_WITH_BALANCE, input_line) != None
        is_new_transaction = re.search(REGEX_TRANSACTION, input_line) != None
        is_end_of_page = re.search(REGEX_END_OF_PAGE, input_line) != None
        is_reading_transaction = curr_transaction != None
        #print('[line] isNewTransaction={} isEndOfPage={} isReadingTransaction={} "{}"'.format(is_new_transaction, is_end_of_page, is_reading_transaction, input_line))

        if is_closing_balance:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)
            parsed_input = re.search(REGEX_CLOSING_BALANCE, input_line).groups()
            curr_transaction = Transaction('', '', parsed_input[0], '0.00', parsed_input[1])

        elif is_new_transaction:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)
            transaction_regex = REGEX_TRANSACTION_WITH_BALANCE if is_new_transaction_with_balance else REGEX_TRANSACTION
            parsed_input = re.search(transaction_regex, input_line).groups()
            curr_transaction = Transaction(
                    parsed_input[0], parsed_input[1],
                    parsed_input[2], parsed_input[3],
                    parsed_input[4] if is_new_transaction_with_balance else '' 
            )
            #print(str(curr_transaction))

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
    
def generate_csv(file_to_save, transactions_list):
    output_data = CSV_HEADER + '\n'

    for transaction in transactions_list:
        change_is_debited = transaction.changes[0] == '-'
        csv_line = '{},{},{},{},,{}' if change_is_debited else '{},{},{},,{},{}'
        output_data += csv_line.format(transaction.date_received, transaction.date_processed, transaction.description, transaction.changes, transaction.balance) + '\n'

    save_str_to_file(file_to_save, output_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='ConvertBankStatementPDFTextExportToCSV',
            description='This script aims to extract the desired transaction data from the Okular exported text file and convert it into a CSV format.')
    parser.add_argument('-i', '--input-filename', required=True)
    parser.add_argument('-o', '--output-filename', required=True)

    args = parser.parse_args()
    print(args.input_filename, args.output_filename)

    transactions_list = convert_input_into_transactions_list(args.input_filename)
    generate_csv(args.output_filename, transactions_list)