
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance      

    def deposit(self, amount):
        self.__balance += amount

    def withdraw(self, amount):
        if amount <= self.__balance:
            self.__balance -= amount
        else:
            print("Insufficient Balance")

    def get_balance(self):
        return self.__balance


account = BankAccount(5000)

account.deposit(1000)
account.withdraw(2000)

print("Balance:", account.get_balance())

