import argparse
from datetime import datetime
import re
from file_io import load_file_to_str, save_str_to_file

class Transaction:
    def __init__(self, date_received, date_processed, description, changes, balance, year):
        self.date_received = date_received
        self.date_processed = date_processed
        self.description = description.strip().replace(',', ' ')
        self.changes = changes.replace(',', '')
        self.balance = balance.replace(',', '')

    def __str__(self) -> str:
        return '{} {} - \"{}\": {} ({})'.format(self.date_received, self.date_processed, self.description, self.changes, self.balance)

############################################################
# MYBOQ / ME GO BANK STATEMENT PROCESSING                  #
############################################################
def change_myboq_date_to_ymd_format(date, year):
    if date == '':
        return date
    return datetime.strptime(date.replace('Sept', 'Sep') + ' ' + year, '%d %b %Y').strftime('%Y-%m-%d')

def convert_myboq_input_into_transactions_list(file_to_load, current_year, is_debugging=False, is_using_legacy_format=False):
    REGEX_DATE_MYBOQ = r'([0-9]{2}-[A-Z][a-z]{2})'
    #REGEX_DATE_MYBOQ = r'([0-9]{1,2} [A-Z][a-z]{2,3})'
    REGEX_DESCRIPTION = r'(.+?)'
    REGEX_AMOUNT_MYBOQ = r'([0-9.,-]+)'
    REGEX_TRANSACTION_MYBOQ = REGEX_DATE_MYBOQ + r'\s+' + REGEX_DATE_MYBOQ + r'\s{2,}' + REGEX_DESCRIPTION + r'\s{2,}' + REGEX_AMOUNT_MYBOQ # This accounts for transactions where the balance is blank (e.g. when it reaches $0.00)
    REGEX_TRANSACTION_WITH_BALANCE_MYBOQ = REGEX_TRANSACTION_MYBOQ + r'\s+' + REGEX_AMOUNT_MYBOQ
    # Full regex: ([0-9]{2}-[A-Z][a-z]{2})\s+([0-9]{2}-[A-Z][a-z]{2})\s{2,}(.+)\s{2,}([0-9.,-]+)\s{2,}([0-9.,-]+)
    # For matching just the dates: ([0-9]{2}-[A-Z][a-z]{2})\s+([0-9]{2}-[A-Z][a-z]{2})

    REGEX_LEGACY_DATE_MYBOQ = r'([0-9]{1,2} [A-Z][a-z]{2})'
    REGEX_LEGACY_TRANSACTION_MYBOQ = REGEX_LEGACY_DATE_MYBOQ + r'\s+' + REGEX_LEGACY_DATE_MYBOQ + r'\s{2,}' + REGEX_DESCRIPTION + r'\s{2,}' + REGEX_AMOUNT_MYBOQ + r'\s{2,}' + REGEX_AMOUNT_MYBOQ + r'\s{2,}' + REGEX_AMOUNT_MYBOQ

    REGEX_CLOSING_BALANCE_MYBOQ = r'(Closing Balance)\s+' + REGEX_AMOUNT_MYBOQ
    REGEX_END_OF_PAGE_MYBOQ = r'(Page|Statement continues over|Bank of Queensland|Please check your|Remember to retain|mebank|Account security tips|•)'

    if is_debugging and is_using_legacy_format: print('Will use legacy format')

    input_data = load_file_to_str(file_to_load).split('\n')
    curr_transaction = None
    transactions_list = []

    for input_line in input_data:
        if len(input_line) == 0:
            continue

        is_closing_balance = re.search(REGEX_CLOSING_BALANCE_MYBOQ, input_line) != None
        is_new_transaction_with_balance = re.search(REGEX_TRANSACTION_WITH_BALANCE_MYBOQ, input_line) != None
        is_new_transaction = re.search(REGEX_TRANSACTION_MYBOQ, input_line) != None
        is_new_legacy_transaction = re.search(REGEX_LEGACY_TRANSACTION_MYBOQ, input_line) != None
        is_end_of_page = re.search(REGEX_END_OF_PAGE_MYBOQ, input_line) != None
        is_reading_transaction = curr_transaction != None
        if is_debugging:
            if is_using_legacy_format:
                print('[line] isNewTxn={} isEndOfPage={} isReadingTxn={} isNewLegacyTxn={} "{}"'.format(is_new_transaction, is_end_of_page, is_reading_transaction, is_new_legacy_transaction, input_line))
            else:
                print('[line] isNewTxn={} isEndOfPage={} isReadingTxn={} isNewTxnWithoutBalance={} isNewTxn={} "{}"'.format(is_new_transaction, is_end_of_page, is_reading_transaction, is_new_transaction, is_new_transaction_with_balance, input_line))

        if is_closing_balance:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)
            parsed_input = re.search(REGEX_CLOSING_BALANCE_MYBOQ, input_line).groups()
            curr_transaction = Transaction('', '', parsed_input[0], '0.00', parsed_input[1], current_year)
            if is_debugging: print('TRANSACTION: {}'.format(str(curr_transaction)))

        elif is_new_transaction:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)
            transaction_regex = REGEX_TRANSACTION_WITH_BALANCE_MYBOQ if is_new_transaction_with_balance else REGEX_TRANSACTION_MYBOQ            

            parsed_input = re.search(transaction_regex, input_line).groups()            

            date_received = change_myboq_date_to_ymd_format(parsed_input[0].replace('-', ' '), current_year)
            date_processed = change_myboq_date_to_ymd_format(parsed_input[1].replace('-', ' '), current_year)
            curr_transaction = Transaction(
                date_received, date_processed,
                parsed_input[2], parsed_input[3],
                parsed_input[4] if is_new_transaction_with_balance else '0.00',
                current_year
            )
            if is_debugging: print('TRANSACTION: {}'.format(str(curr_transaction)))

        elif is_using_legacy_format and is_new_legacy_transaction:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)
            transaction_regex = REGEX_LEGACY_TRANSACTION_MYBOQ

            parsed_input = re.search(transaction_regex, input_line).groups()
            
            date_received = change_myboq_date_to_ymd_format(parsed_input[0].replace('-', ' '), current_year)
            date_processed = change_myboq_date_to_ymd_format(parsed_input[1].replace('-', ' '), current_year)

            debits = parsed_input[3]
            credits = parsed_input[4]
            changes = '-' + debits if credits == '0.00' else credits
            curr_transaction = Transaction(
                date_received, date_processed,
                parsed_input[2], changes,
                parsed_input[5],
                current_year
            )
            if is_debugging: print('TRANSACTION: {}'.format(str(curr_transaction)))

        elif is_reading_transaction:
            if is_end_of_page:
                transactions_list.append(curr_transaction)
                curr_transaction = None
                continue
            curr_transaction.description += ' ' + input_line.replace(',', ' ').strip()

        else:
            curr_transaction = None
            continue

    print('And the final result shall be:')
    [print(transaction) for transaction in transactions_list]
    print(len(transactions_list))

    return transactions_list
    
def generate_myboq_csv(transactions_list, file_to_save, is_reversed=False):
    CSV_HEADER_MYBOQ = 'Date,Processed,Description,Debits ($),Credits ($),Balance ($)'

    file_to_save = file_to_save.replace('.txt', '.csv')
    output_data = CSV_HEADER_MYBOQ + '\n'

    transactions_list = reversed(transactions_list) if is_reversed else transactions_list

    for transaction in transactions_list:
        change_is_debited = transaction.changes[0] == '-'
        csv_line = '{},{},{},{},,{}' if change_is_debited else '{},{},{},,{},{}'
        output_data += csv_line.format(transaction.date_received, transaction.date_processed, transaction.description, transaction.changes, transaction.balance) + '\n'

    save_str_to_file(file_to_save, output_data)

############################################################
# VIRGIN MONEY BANK STATEMENT PROCESSING                   #
############################################################
def change_virgin_date_to_ymd_format(date):
    if date == '':
        return date
    return datetime.strptime(date, '%d/%m/%y').strftime('%Y-%m-%d')

def convert_virgin_input_into_transactions_list(file_to_load, current_year, is_debugging=False):
    REGEX_DATE_VIRGIN = r'([0-9]{2}\/[0-9]{2}\/[0-9]{2})'
    REGEX_DESCRIPTION = r'(.+?)'
    REGEX_AMOUNT_VIRGIN = r'\$([0-9]+\.[0-9]{2})'
    REGEX_CR_DR = r'([CD]r)'
    REGEX_TRANSACTION_VIRGIN = REGEX_DATE_VIRGIN + r'\s+' + REGEX_DATE_VIRGIN + r'\s{2,}' + REGEX_DESCRIPTION + r'\s{2,}' + REGEX_AMOUNT_VIRGIN + ' ' + REGEX_CR_DR

    REGEX_END_OF_PAGE_VIRGIN = r'(Page|•)'

    input_data = load_file_to_str(file_to_load).split('\n')
    curr_transaction = None
    transactions_list = []

    for input_line in input_data:
        if len(input_line) == 0:
            continue

        is_new_transaction = re.search(REGEX_TRANSACTION_VIRGIN, input_line) != None
        is_end_of_page = re.search(REGEX_END_OF_PAGE_VIRGIN, input_line) != None
        is_reading_transaction = curr_transaction != None
        if is_debugging:
            print('[line] isNewTxn={} isEndOfPage={} isReadingTxn={} isNewTxn={} "{}"'.format(is_new_transaction, is_end_of_page, is_reading_transaction, is_new_transaction, input_line))

        if is_new_transaction:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)

            parsed_input = re.search(REGEX_TRANSACTION_VIRGIN, input_line).groups()            

            date_processed = change_virgin_date_to_ymd_format(parsed_input[0])
            date_received = change_virgin_date_to_ymd_format(parsed_input[1])
            amount = ('-' if parsed_input[4] == 'Dr' else '') + parsed_input[3]

            curr_transaction = Transaction(
                date_received, date_processed,
                parsed_input[2], amount,
                '',
                current_year
            )
            if is_debugging: print('TRANSACTION: {}'.format(str(curr_transaction)))
        elif is_reading_transaction:
            if is_end_of_page:
                transactions_list.append(curr_transaction)
                curr_transaction = None
                continue
            curr_transaction.description += ' ' + input_line.replace(',', ' ').strip()

        else:
            curr_transaction = None
            continue

    print('And the final result shall be:')
    [print(transaction) for transaction in transactions_list]
    print(len(transactions_list))

    return transactions_list
    
def generate_virgin_csv(transactions_list, file_to_save, is_reversed=False):
    CSV_HEADER_VIRGIN = 'Processed Date,Transaction Date,Details,Amount'

    file_to_save = file_to_save.replace('.txt', '.csv')
    output_data = CSV_HEADER_VIRGIN + '\n'

    transactions_list = reversed(transactions_list) if is_reversed else transactions_list

    for transaction in transactions_list:
        csv_line = '{},{},{},{}'
        output_data += csv_line.format(transaction.date_processed, transaction.date_received, transaction.description, transaction.changes) + '\n'

    save_str_to_file(file_to_save, output_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='ConvertBankStatementPDFTextExportToCSV',
            description='This script aims to extract the desired transaction data from the Okular exported text file and convert it into a CSV format.')
    parser.add_argument('-f', '--filename', required=True, help='Filename of the text file to convert to CSV')
    parser.add_argument('-t', '--type', required=True, help='Type of bank statement to process. Valid values: myboq, virgin')
    parser.add_argument('-y', '--year', required=True, help='The current year to add to the transaction date. Required for MyBOQ format type')
    parser.add_argument('-r', '--reverse', action='store_true', help='If provided, reverse the output')
    parser.add_argument('-l', '--legacy', action='store_true', help='If provided, process the file using the pre-2024 format, in which the date is 1 Jan instead of 01-Jan and the zero balance is always provided')
    parser.add_argument('-d', '--debug', action='store_true', help='If provided, enable transaction debugging output')

    args = parser.parse_args()
    print(args)

    if args.type == 'myboq':
        transactions_list = convert_myboq_input_into_transactions_list(args.filename, args.current_year, args.debug, args.legacy)
        generate_myboq_csv(transactions_list, args.filename, args.reverse)
    elif args.type == 'virgin':
        transactions_list = convert_virgin_input_into_transactions_list(args.filename, args.current_year, args.debug)
        generate_virgin_csv(transactions_list, args.filename, args.reverse)
    else:
        print('Should not happen')