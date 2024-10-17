from django.shortcuts import render, redirect
from .utils import random_AccountNumGen
from django.contrib.auth.models import Group
from django.http import HttpResponse
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from .forms import CreateUserForm, AccountForm, FundForm, StockForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.


def home(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def market(request):
    stocks = Stock.objects.all()
    
    
    for stock in stocks:
        stock.generateRandCost()  

    context = {'stocks': stocks}
    return render(request, 'market.html', context)

@unauthenticated_user
def loginPage(request):
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    
                    if user.groups.filter(name='admin').exists():
                        return redirect('adminpanel')
                    
                    return redirect('userpanel')
                else:
                    messages.error(request, 'Invalid username or password')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            form = AuthenticationForm()

        context = {'form': form}
        return render(request, 'login.html', context)

@unauthenticated_user
def registerPage(request):
    if request.method == 'POST':

        form1 = CreateUserForm(request.POST)
        form2 = AccountForm(request.POST)

        if form1.is_valid() and form2.is_valid():
            newUser = form1.save()
            
            if newUser.is_superuser or newUser.is_staff:
                messages.error(request, 'Cannot create an account for a superuser or admin.')
                return redirect('register')
            
            group = Group.objects.get(name='customer')
            newUser.groups.add(group)

            userAccountNumber = random_AccountNumGen()
            phoneNumber = form2.cleaned_data.get('phoneNumber')

            newAccount = Account.objects.create(
                user=newUser, accountNumber=userAccountNumber, phoneNumber=phoneNumber
            )
            
            Portfolio.objects.create(
                account=newAccount, balance=0
            )

            username = form1.cleaned_data.get('username')

            messages.success(request, f'Account was created for {username}')
            return redirect('login')
    else:
        form1 = CreateUserForm()
        form2 = AccountForm()

    context = {'form1': form1, 'form2': form2}
    return render(request, 'register.html', context)


def logoutPage(request):
    logout(request)
    messages.success(request,' Successfully Logged out')
    return redirect('login')

####################
#customer views
####################
@allowed_users(allowed_roles=['customer'])   
def userPanel(request):
    stocks = Stock.objects.all()
    for stock in stocks:
        stock.getStockCost()
    
    if hasattr(request.user, 'account') and hasattr(request.user.account, 'portfolio'):
        name = request.user.first_name
        balance = request.user.account.portfolio.balance
        purchased_stock = request.user.account.portfolio.purchased_stock()
        
        print('Current Balance: ', balance)
    else:
        balance = None
        print('No portfolio or account associated with this user.')
        
    context = {'balance':balance, 'name':name, 'purchased_stock': purchased_stock, 'stocks': stocks}
    return render(request, 'userpanel.html', context)


@allowed_users(allowed_roles=['customer'])
def funds(request):
    user_portfolio = request.user.account.portfolio

    if request.method == 'POST':
        form = FundForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data.get('action')
            amount = form.cleaned_data.get('balance')

            if action == 'deposit':
                user_portfolio.balance += amount 
                messages.success(request, f'You have successfully deposited ${amount}.')

                
                transaction = Transaction.objects.create(
                    portfolio=user_portfolio,
                    transactionType='Deposit',
                    quantity=amount
                )
               
                total_amount = transaction.total_cost()
                messages.success(request, f'Total amount for this transaction: ${total_amount}.')

            elif action == 'withdraw':
                if user_portfolio.balance >= amount:
                    user_portfolio.balance -= amount 
                    messages.success(request, f'You have successfully withdrawn ${amount}.')

                    
                    transaction = Transaction.objects.create(
                        portfolio=user_portfolio,
                        transactionType='Withdraw',
                        quantity=amount
                    )
                    
                    total_amount = transaction.total_cost()
                    messages.success(request, f'Total amount for this transaction: ${total_amount}.')
                    
                else:
                    messages.error(request, 'Insufficient funds for withdrawal.')

            user_portfolio.save()
            return redirect('userpanel')
    else:
        form = FundForm()

    context = {'form': form}
    return render(request, 'funds.html', context)


@allowed_users(allowed_roles=['customer'])
def transactions(request):
    user_portfolio = request.user.account.portfolio
    
    transactions = Transaction.objects.filter(portfolio=user_portfolio).order_by('-datePurchased')

    context = {
        'transactions': transactions,
    }
    
    return render(request, 'transactions.html', context)

@allowed_users(allowed_roles=['customer'])
def stockmarket(request):
    stocks = Stock.objects.all()
    for stock in stocks:
        stock.generateRandCost()   ##change this

    form = StockForm()

    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.pricePurchased = transaction.stock.price
            action = form.cleaned_data['action']

           
            portfolio = request.user.account.portfolio  

            if action == 'buy':
                transaction.transactionType = 'Buy'
            elif action == 'sell':
                transaction.transactionType = 'Sell'

            transaction.portfolio = portfolio 

            # Check portfolio balance before saving the transaction
            if portfolio:
                if action == 'buy':
                    total_cost = transaction.pricePurchased * transaction.quantity
                    if portfolio.balance >= total_cost:
                        portfolio.balance -= total_cost  
                        transaction.save()
                        print('Transaction was successful')
                        return redirect('userpanel')
                    else:
                        print('Insufficient funds')
                elif action == 'sell':
                    if portfolio.purchased_stock().get(transaction.stock.ticker, 0) >= transaction.quantity:
                        transaction.save()
                        print('Transaction was successful')
                        return redirect('userpanel')
                    else:
                        print('Not enough stock to sell')
            else:
                print('Portfolio not found')
        else:
            print('Form is not valid')
            
        print('Transaction was not completed')
        form = StockForm()

    context = {'stocks': stocks, 'form': form}
    return render(request, 'stockmarket.html', context)





####################
#admin views
####################
@allowed_users(allowed_roles=['admin'])   
def adminPanel(request):
    return render(request, 'adminpanel.html')

@allowed_users(allowed_roles=['admin'])   
def markethours(request):
    return render(request, 'markethours.html')

@allowed_users(allowed_roles=['admin'])   
def stockcreation(request):
    return render(request, 'stockcreation.html')

@allowed_users(allowed_roles=['admin'])   
def stockdeletion(request):
    return render(request, 'stockdeletion.html')