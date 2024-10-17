from django.contrib.auth.models import User
from django.db import models


from django.utils import timezone
import random
from decimal import Decimal

# Create your models here.


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    accountNumber = models.IntegerField(unique=True)
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"User {self.user.username}: Account {self.accountNumber}"


class Stock(models.Model):
    stockName = models.CharField(max_length=15, null=True)
    ticker = models.CharField(max_length=4, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    maxPrice = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    minPrice = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    volumeQty = models.IntegerField(null=True)
    remainingVol = models.IntegerField(null=True)
    priceTime = models.DateTimeField(default=timezone.now)
    
    def getStockCost(self):
        self.generateRandCost()
        return "{:.2f}".format(self.price)

    def generateRandCost(self):
        currentTime = timezone.now()
        timeDiff = currentTime - self.priceTime
        diffMin = timeDiff.total_seconds() / 60
        if diffMin >= 15:  # Adjust this value for frequency of price updates
            
            random_number = Decimal(random.uniform(-0.45, 0.45))
            self.priceTime = currentTime
            self.price += (self.price * random_number)
            
            if self.minPrice is None:
                self.minPrice = self.price
            if self.maxPrice is None:
                self.maxPrice = self.price

        # Now you can safely compare minPrice and maxPrice
            if self.price <= self.minPrice:
                self.minPrice = self.price
            if self.price >= self.maxPrice:
                self.maxPrice = self.price
        
            self.save()

    def market_capitalization(self):
        if self.volumeQty and self.price is not None:
            return self.volumeQty * self.price
        return 0.0

    def __str__(self):
        return self.ticker


class Portfolio(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Account {self.account} Balance {self.balance}"

    def purchased_stock(self):
        transactions = Transaction.objects.filter(portfolio=self)
        stockQuantities = {}

        for transaction in transactions:
            stock = transaction.stock
            if stock:
                if transaction.transactionType in ['Buy', 'Deposit']:
                    stockQuantities[stock.ticker] = stockQuantities.get(
                        stock.ticker, 0) + transaction.quantity
                elif transaction.transactionType == 'Sell':
                    stockQuantities[stock.ticker] = stockQuantities.get(
                        stock.ticker, 0) - transaction.quantity

        purchased_stocks = [{'ticker': ticker, 'quantity': quantity}
                            for ticker, quantity in stockQuantities.items() if quantity > 0]
        return purchased_stocks


class Transaction(models.Model):
    type = (
        ('Deposit', 'Deposit'),
        ('Withdraw', 'Withdraw'),
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )

    portfolio = models.ForeignKey(
        Portfolio, null=True, on_delete=models.SET_NULL)
    stock = models.ForeignKey(Stock, null=True, on_delete=models.SET_NULL)
    transactionType = models.CharField(max_length=9, null=True, choices=type)
    quantity = models.IntegerField()
    pricePurchased = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    datePurchased = models.DateTimeField(auto_now_add=True, null=True)

    def total_cost(self):
        if self.transactionType in ['Deposit', 'Withdraw']:
            return self.quantity
        elif self.transactionType in ['Buy', 'Sell']:
            return self.pricePurchased * self.quantity if self.pricePurchased else 0
        return 0.0

    def __str__(self):
        return f"portfolio {self.portfolio} stock {self.stock} date {self.datePurchased}"


class ContactMessage(models.Model):
    date = models.DateTimeField(auto_now_add=True, null=True)
    email = models.CharField(max_length=20, blank=True, null=True)
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)
    subject = models.TextField(max_length=200)
