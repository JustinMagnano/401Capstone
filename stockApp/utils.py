import random
from . models import Account


def random_AccountNumGen():
    while True:
        randomNum = random.randint(100000, 999999)

        if not Account.objects.filter(accountNumber=randomNum).exists():
            return randomNum
