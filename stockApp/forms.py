from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['phoneNumber']


class FundForm(forms.ModelForm):
    ACTION_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]

    action = forms.ChoiceField(choices=ACTION_CHOICES)
    balance = forms.DecimalField(min_value=0.01, decimal_places=2, max_digits=10)

    class Meta:
        model = Portfolio
        fields = ['balance']
        labels = {'balance': 'amount'}

    def clean_amount(self):
        balance = self.cleaned_data.get('balance')

        if balance <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return balance


from django import forms
from .models import Transaction

class StockForm(forms.ModelForm):
    ACTION_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    action = forms.ChoiceField(choices=ACTION_CHOICES, label='Action')
    quantity = forms.IntegerField(
        label='Quantity',
        min_value=1,  
        widget=forms.NumberInput(attrs={'min': 1}) 
    )

    class Meta:
        model = Transaction
        fields = ['stock', 'quantity', 'action']
        labels = {
            'stock': 'Stock',
        }

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        quantity = cleaned_data.get('quantity')
        portfolio = self.initial.get('portfolio')
        stock = cleaned_data.get('stock')

        if action == 'buy' and stock and portfolio:
            if quantity is None:
                raise forms.ValidationError('Quantity is required for buying stocks.')
            total_cost = stock.price * quantity
            if portfolio.balance < total_cost:
                raise forms.ValidationError(
                    f'Insufficient funds. You need {total_cost:.2f} but have {portfolio.balance:.2f}.'
                )

        if action == 'sell' and stock and portfolio:
            if quantity is None:
                raise forms.ValidationError('Quantity is required for selling stocks.')
            if portfolio.get_stock_quantity(stock) < quantity:
                raise forms.ValidationError(
                    f'You only own {portfolio.get_stock_quantity(stock)} shares of {stock}.'
                )

        return cleaned_data


class MarketHoursForm(forms.ModelForm):
    class Meta:
        model = MarketHours
        fields = ['openTime', 'closeTime']
        widgets = {
            'openTime': forms.TimeInput(attrs={'type': 'time'}),
            'closeTime': forms.TimeInput(attrs={'type': 'time'}),
        }


class HolidaysForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget)
    description = forms.CharField(max_length=20)
    
    
class HolidaysDeletionForm(forms.Form):
    holidays = forms.ModelChoiceField(
        queryset=Holidays.objects.all(),
        empty_label="Select a Holiday to delete",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class MarketdayForm(forms.Form):
    class Meta:
        model = MarketDay
        fields = ['weekdays', 'status']


class ModifyStockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['stockName', 'ticker', 'price', 'volumeQty']
        labels = {
            'stockName': 'Stock Name',
            'ticker': 'Ticker Symbol',
            'price': 'Stock Price',
            'volumeQty': 'Volume Quantity',
        }

    def clean(self):
        cleaned_data = super().clean()
        stockName = cleaned_data.get('stockName')
        ticker = cleaned_data.get('ticker')
        price = cleaned_data.get('price')
        volumeQty = cleaned_data.get('volumeQty')

        if not stockName:
            raise forms.ValidationError('Stock name must be provided.')

        if not ticker:
            raise forms.ValidationError('Ticker must be provided.')

        if price is None or price <= 0:
            raise forms.ValidationError(
                'Stock price must be a positive value.')

        if volumeQty is None or volumeQty <= 0:
            raise forms.ValidationError(
                'Volume quantity must be a positive value.')

        return cleaned_data



class StockDeletionForm(forms.Form):
    stock = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        empty_label="Select a stock to delete",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class StockPriceAdjustmentForm(forms.Form):
    stock = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        empty_label="Select a stock to update the price",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter new price'}),
        label='Stock Price'
    )

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')

        if price is None or price <= 0:
            raise forms.ValidationError(
                'Stock price must be a positive value.')
        return cleaned_data


class MessageForm(forms.ModelForm):
    email = forms.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9@._+-]+$',
            message='Email contains illegal characters.'
        )]
    )
    phoneNumber = forms.CharField(
        max_length=15, required=False,
        validators=[RegexValidator(
            regex=r'^[0-9+()-]+$',
            message='Phone number contains illegal characters.'
        )]
    )
    subject = forms.CharField(
        max_length=200,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9 .,!?"\'-]+$',
            message='Subject contains illegal characters.'
        )]
    )

    class Meta:
        model = ContactMessage
        fields = ['email', 'phoneNumber', 'subject']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phoneNumber = cleaned_data.get('phoneNumber')
        subject = cleaned_data.get('subject')

        if email and len(email) < 5:
            self.add_error('email', 'Email must be at least 5 characters long.')

        if phoneNumber and not phoneNumber.isdigit():
            self.add_error('phoneNumber', 'Phone number must contain only digits.')

        if subject and len(subject) < 10:
            self.add_error('subject', 'Subject must be at least 10 characters long.')

        return cleaned_data
    
