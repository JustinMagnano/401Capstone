from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import random
from decimal import Decimal, ROUND_DOWN
from datetime import datetime, time, date
import calendar
from django.core.validators import MinValueValidator

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
            self.price = self.price.quantize(Decimal('0.00'), rounding=ROUND_DOWN)  

            if self.minPrice is None:
                self.minPrice = self.price
            elif self.price < self.minPrice:
                self.minPrice = self.price

            if self.maxPrice is None:
                self.maxPrice = self.price
            elif self.price > self.maxPrice:
                self.maxPrice = self.price

            self.minPrice = self.minPrice.quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            self.maxPrice = self.maxPrice.quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            self.save()

    def market_capitalization(self):
        if self.volumeQty and self.price is not None:
            return self.volumeQty * self.price
        return 0.0

    def __str__(self):
        return self.ticker


class Portfolio(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Account {self.account} Balance {self.balance}"

    def purchased_stock(self):
        transactions = Transaction.objects.filter(portfolio=self)
        stockQuantities = {}

        for transaction in transactions:
            stock = transaction.stock
            if stock:
                if transaction.transactionType in ['Buy', 'Deposit']:
                    stockQuantities[stock.ticker] = stockQuantities.get(stock.ticker, 0) + transaction.quantity
                elif transaction.transactionType == 'Sell':
                    stockQuantities[stock.ticker] = stockQuantities.get(stock.ticker, 0) - transaction.quantity

        stockQuantities = {ticker: quantity for ticker, quantity in stockQuantities.items() if quantity > 0}

        return stockQuantities


class Transaction(models.Model):
    type = (
        ('Deposit', 'Deposit'),
        ('Withdraw', 'Withdraw'),
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )

    portfolio = models.ForeignKey(Portfolio, null=True, on_delete=models.SET_NULL)
    stock = models.ForeignKey(Stock, null=True, on_delete=models.SET_NULL)
    transactionType = models.CharField(max_length=9, null=True, choices=type)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    pricePurchased = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    datePurchased = models.DateTimeField(auto_now_add=True, null=True)

    def total_cost(self):
        quantitydecimal = Decimal(self.quantity)

        if self.transactionType in ['Deposit', 'Withdraw']:
            return quantitydecimal.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        elif self.transactionType in ['Buy', 'Sell']:
            if self.pricePurchased:
                result = self.pricePurchased * quantitydecimal
                return result.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        return Decimal('0.00')

    def __str__(self):
        return f"portfolio {self.portfolio} stock {self.stock} date {self.datePurchased}"


class ContactMessage(models.Model):
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True)
    email = models.CharField(max_length=20, blank=False, null=False)
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)
    subject = models.TextField(max_length=200)
    
    def __str__(self):
        return (f'{self.date}: {self.email}')


class MarketHours(models.Model):
    openTime = models.TimeField()
    closeTime = models.TimeField()
    
    class Meta:
        verbose_name = 'Market Hours'
        verbose_name_plural = 'Market Hours'
  
    
    def get_hours(self):
        return {'openTime': self.openTime, 'closeTime': self.closeTime}

    def set_hours(self, openTime, closeTime):
        self.openTime = openTime
        self.closeTime = closeTime

    def is_market_open(self, currentTime):
        if self.openTime is None or self.closeTime is None:
            return False 
        
        return self.openTime <= currentTime <= self.closeTime

    def is_trading_day(self):
        currentDay = datetime.today().strftime('%A')
        try:
            marketDay = MarketDay.objects.get(weekday=currentDay)
            return marketDay.status
        except MarketDay.DoesNotExist:
            return False

    def can_trade(self, currentTime):
        if not self.is_trading_day():
            return False
        return self.is_market_open(currentTime)


class Holidays(models.Model):
    date = models.DateField(unique=True)
    description = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return (f'{self.date} - {self.description}')


class MarketDay(models.Model):
    choices = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    status = models.BooleanField()
    weekday = models.CharField(max_length=9, choices=choices, unique=True)

    def __str__(self):
        return self.weekday
