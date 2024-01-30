import random
import string


def generate_cards(card_dropping_quantity: int) -> list:
    """ New cards generator """
    card_codes = [''.join(random.choice(string.ascii_letters + string.digits) for i in range(7)) for i in
                  range(card_dropping_quantity)]
    return card_codes



