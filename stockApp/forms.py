from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import Transaction, Account, Portfolio, Stock


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
    
    class Meta:
        model = Portfolio
        fields = ['balance']
        labels = {'balance': 'amount'}
        
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount
    
class StockForm(forms.ModelForm):
    ACTION_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES, label='Action')
    
    class Meta:
        model = Transaction
        fields = ['stock', 'quantity', 'action']  # Exclude portfolio if set in view
        labels = {
            'stock': 'Stock',
            'quantity': 'Quantity',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        quantity = cleaned_data.get('quantity')
        portfolio = self.initial.get('portfolio')  
        stock = cleaned_data.get('stock')

        if action == 'buy' and stock and portfolio:
            total_cost = stock.price * quantity
            if portfolio.balance < total_cost:
                raise forms.ValidationError(f'Insufficient funds. You need {total_cost} but have {portfolio.balance}.')

        if action == 'sell' and stock and portfolio:
            if portfolio.get_stock_quantity(stock) < quantity:
                raise forms.ValidationError(f'You only own {portfolio.get_stock_quantity(stock)} shares of {stock}.')

        return cleaned_data
