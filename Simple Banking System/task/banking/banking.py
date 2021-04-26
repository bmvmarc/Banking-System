import random
import sqlite3


def create_table():
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS card (
                        id	INTEGER PRIMARY KEY AUTOINCREMENT,
                        number	TEXT,
                        pin	TEXT,
                        balance	INTEGER DEFAULT 0
                    )
                    ''')

    connection.commit()


def find_card(number):
    cursor.execute('SELECT pin, balance from card WHERE number = ?', (number,))
    row = cursor.fetchone()
    if row is None:
        return None
    else:
        pin = row[0]
        balance = row[1]

    return {"number": number, "pin": pin, "balance": balance}


def create_card():
    cursor.execute('SELECT max(id) from card')
    row = cursor.fetchone()
    if row[0] is None:
        num = 1
    else:
        num = row[0] + 1

    number = "400000" + str(num).rjust(9, '0')

    number += get_the_check_figure(number)

    pin = str(random.randint(1, 9999)).rjust(4, '0')

    cursor.execute('INSERT INTO card (number, pin) VALUES (?,?)', (number, pin))
    connection.commit()
    return {'number': number, 'pin': pin}


def add_income(card_number, input_income):
    cursor.execute('SELECT balance FROM card WHERE number = ?', (card_number,))
    row = cursor.fetchone()
    cur_balance = row[0]
    new_balance = cur_balance + input_income
    cursor.execute('UPDATE card SET balance = ? WHERE number = ?', (new_balance, card_number))
    connection.commit()
    return new_balance


def close_account(card_info):
    cursor.execute('DELETE FROM card WHERE number = ?', (card_info['number'],))
    connection.commit()


def get_the_check_figure(number):
    s = 0
    for i in range(15):
        n = int(number[i])
        if i % 2 == 0:
            n = n * 2
            n = n if n < 10 else n - 9
        s += n

    return str(-(s % 10 - 10))[-1]


def do_transfer(card_info, card2_number, amount):
    card_info['balance'] = add_income(card_info['number'], -amount)
    add_income(card2_number, amount)


def main_menu():
    entry = None

    while entry != '0':

        entry = input("\n1. Create an account\n2. Log into account\n0. Exit\n")

        if entry == '1':
            card = create_card()
            print(
                '\nYour card has been created\nYour card number:\n{}\nYour card PIN:\n{}'.format(card['number'],
                                                                                                 card['pin']))

        if entry == '2':
            input_card_number = input('\nEnter your card number:\n')
            input_pin = input('Enter your PIN:\n')
            found = find_card(input_card_number)
            if found is not None and input_pin == found['pin']:
                print('\nYou have successfully logged in!')
                entry = menu_logged_in(found)
            else:
                print('\nWrong card number or PIN!')


def menu_logged_in(card_info):
    entry = None
    while entry != '0':
        entry = input("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")

        if entry == '1':
            print('Balance: {}'.format(card_info['balance']))

        if entry == '2':  # Add income
            input_income = int(input('\nEnter income:\n'))
            card_info['balance'] = add_income(card_info['number'], input_income)
            print('\nIncome was added!')

        if entry == '3':  # Transfer
            input_card2_number = input('\nTransfer\nEnter card number:\n')

            if input_card2_number == card_info['number']:
                print("\nYou can't transfer money to the same account!")
            elif input_card2_number[-1] != get_the_check_figure(input_card2_number):
                print('\nProbably you made a mistake in the card number. Please try again!')
            elif find_card(input_card2_number) is None:
                print('\nSuch a card does not exist.')
            else:
                input_amount = int(input('\nEnter how much money you want to transfer:\n'))
                if input_amount > card_info['balance']:
                    print('\nNot enough money!')
                else:
                    do_transfer(card_info, input_card2_number, input_amount)
                    print('\nSuccess!')

        if entry == '4':  # Close account
            close_account(card_info)
            print('\nThe account has been closed!')
            break

        if entry == '5':
            print('\nYou have successfully logged out!')
            break

    return entry


connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()
create_table()

main_menu()

connection.close()
