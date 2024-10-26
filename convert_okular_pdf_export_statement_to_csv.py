import re
from file_io import load_file_to_str, save_str_to_file

CSV_HEADER = 'Date,Processed,Description,Debits ($),Credits ($),Balance ($)'
REGEX_DATE = r'([0-9]{2}-[A-Z][a-z]{2})'
REGEX_DESCRIPTION = r'(.+)'
REGEX_AMOUNT = r'([0-9.,-]+)'
REGEX_TRANSACTION = REGEX_DATE + r'\s+' + REGEX_DATE + r'\s{2,}' + REGEX_DESCRIPTION + r'\s{2,}' + REGEX_AMOUNT + r'\s{2,}' + REGEX_AMOUNT
# ([0-9]{2}-[A-Z][a-z]{2})\s+([0-9]{2}-[A-Z][a-z]{2})

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
        is_new_transaction = re.search(REGEX_TRANSACTION, input_line) != None
        is_end_of_page = re.search(r'(Statement continues over|Bank of Queensland|Page)', input_line) != None
        is_reading_transaction = curr_transaction != None
        print('[line] isNewTransaction={} isEndOfPage={} isReadingTransaction={} "{}"'.format(is_new_transaction, is_end_of_page, is_reading_transaction, input_line))

        if is_new_transaction:
            if is_reading_transaction:
                transactions_list.append(curr_transaction)

            parsed_input = re.search(REGEX_TRANSACTION, input_line).groups()
            curr_transaction = Transaction(parsed_input[0], parsed_input[1], parsed_input[2], parsed_input[3], parsed_input[4])
            print(str(curr_transaction))
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
    transactions_list = convert_input_into_transactions_list('test PDF export - MyBOQ.txt')
    generate_csv('MyBOQ.csv', transactions_list)