from django.shortcuts import render, redirect, get_object_or_404
from .utils import random_AccountNumGen
from django.contrib.auth.models import Group
from django.http import HttpResponse
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session

import calendar
from calendar import HTMLCalendar
from datetime import datetime, time
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta


def home(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            phoneNumber = form.cleaned_data.get('phoneNumber')
            subject = form.cleaned_data.get('subject')

            newMessage = ContactMessage.objects.create(
                email=email,
                phoneNumber=phoneNumber,
                subject=subject

            )
            newMessage.save()
            messages.success(request, ' Thank you for for your feedback')
        else:
            messages.error(
                request, "There is an error with the feedback form.")

    else:
        form = MessageForm()
    context = {'form': form}
    return render(request, 'contact.html', context)


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
                messages.error(
                    request, 'Cannot create an account for a superuser or admin.')
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
    messages.success(request, ' Successfully Logged out')
    return redirect('login')


####################
# customer views
####################
@allowed_users(allowed_roles=['customer'])
def userPanel(request):
    stocks = Stock.objects.all()
    for stock in stocks:
        stock.getStockCost()

    name = request.user.first_name
    balance = None
    purchased_stock = {}

    if hasattr(request.user, 'account') and hasattr(request.user.account, 'portfolio'):
        balance = request.user.account.portfolio.balance
        purchased_stock = request.user.account.portfolio.purchased_stock()
    else:
        print('No portfolio or account associated with this user.')

    context = {
        'balance': balance,
        'name': name,
        'purchased_stock': purchased_stock,
        'stocks': stocks
    }
    return render(request, 'userpanel.html', context)


@allowed_users(allowed_roles=['customer'])
def funds(request):
    user_portfolio = request.user.account.portfolio
    user_balance = user_portfolio.balance

    if request.method == 'POST':
        form = FundForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data.get('action')
            amount = form.cleaned_data.get('balance')

            amount = Decimal(amount).quantize(Decimal('0.01'))

            if action == 'deposit':
                user_portfolio.balance += amount
                messages.success(
                    request, f'You have successfully deposited ${amount}.')

                transaction = Transaction.objects.create(
                    portfolio=user_portfolio,
                    transactionType='Deposit',
                    quantity=amount
                )

                total_amount = transaction.total_cost()
                messages.success(
                    request, f'Total amount for this transaction: ${total_amount}.')

            elif action == 'withdraw':
                if user_portfolio.balance >= amount:
                    user_portfolio.balance -= amount
                    messages.success(
                        request, f'You have successfully withdrawn ${amount}.')

                    transaction = Transaction.objects.create(
                        portfolio=user_portfolio,
                        transactionType='Withdraw',
                        quantity=amount  # Use Decimal for the quantity
                    )

                    total_amount = transaction.total_cost()
                    messages.success(
                        request, f'Total amount for this transaction: ${total_amount}.')
                else:
                    messages.error(
                        request, 'Insufficient funds for withdrawal.')

            user_portfolio.save()
            return redirect('userpanel')
    else:
        form = FundForm()

    context = {'form': form,
               'user_balance': user_balance
               }
    return render(request, 'funds.html', context)


@allowed_users(allowed_roles=['customer'])
def transactions(request):
    user_portfolio = request.user.account.portfolio

    transactions = Transaction.objects.filter(
        portfolio=user_portfolio).order_by('-datePurchased')

    context = {
        'transactions': transactions,
    }

    return render(request, 'transactions.html', context)


@allowed_users(allowed_roles=['customer'])
def stockmarket(request):
    market_hours = MarketHours.objects.first()
    if not market_hours:
        messages.error(request, "Market hours not found.")
        return redirect('userpanel')

    today = datetime.now().date()
    now = datetime.now().time()
    today_weekday = datetime.now().strftime('%A')
    market_day = MarketDay.objects.filter(
        weekday=today_weekday, status=True).first()

    if not market_day or not market_hours.is_market_open(now) or Holidays.objects.filter(date=today).exists():
        messages.error(
            request, "Market is currently closed or not allowed today.")
        return redirect('userpanel')

    stocks = Stock.objects.all()
    for stock in stocks:
        stock.generateRandCost()

    form = StockForm()
    user_portfolio = request.user.account.portfolio
    user_balance = user_portfolio.balance

    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            transaction = create_transaction(form, user_portfolio, request)
            if transaction:
                messages.success(
                    request, f'Transaction was successful. Total amount for this transaction: ${transaction.total_cost:.2f}.')
                return redirect('userpanel')

        else:
            messages.error(request, 'Form validation failed')

    context = {'stocks': stocks, 'form': form, 'user_balance': user_balance}
    return render(request, 'stockmarket.html', context)


def create_transaction(form, portfolio, request):
    transaction = form.save(commit=False)
    transaction.pricePurchased = transaction.stock.price
    action = form.cleaned_data['action']
    transaction.transactionType = action.capitalize()
    transaction.portfolio = portfolio

    total_cost = transaction.pricePurchased * transaction.quantity

    if action == 'buy':
        return handle_buy_transaction(transaction, portfolio, total_cost, request)
    elif action == 'sell':
        return handle_sell_transaction(transaction, portfolio, request)
    else:
        messages.error(request, "Invalid transaction action.")
        return None


def handle_buy_transaction(transaction, portfolio, total_cost, request):
    if transaction.stock.remainingVol >= transaction.quantity:
        if portfolio.balance >= total_cost:
            portfolio.balance -= total_cost
            transaction.stock.remainingVol -= transaction.quantity
            transaction.save()
            transaction.stock.save()
            portfolio.save()
            transaction.total_cost = total_cost
            return transaction
        else:
            messages.error(request, 'Insufficient funds')
    else:
        messages.error(request, 'Not enough stock available to buy')
    return None


def handle_sell_transaction(transaction, portfolio, request):
    purchased_stock_dict = portfolio.purchased_stock()
    purchased_stock_qty = purchased_stock_dict.get(transaction.stock.ticker, 0)

    if purchased_stock_qty >= transaction.quantity:
        total_income = transaction.pricePurchased * transaction.quantity
        portfolio.balance += total_income
        transaction.stock.remainingVol += transaction.quantity
        transaction.save()
        transaction.stock.save()
        portfolio.save()
        transaction.total_cost = total_income
        return transaction
    else:
        messages.error(request, 'Not enough stock to sell')
    return None


####################
# admin views
####################
@allowed_users(allowed_roles=['admin'])
def adminPanel(request):

    today = timezone.now().date()
    transactions_today = Transaction.objects.filter(
        datePurchased__date=today).count()

    thirty_days = timezone.now() - timedelta(days=30)
    transactions_last_30_days = Transaction.objects.filter(
        datePurchased__gte=thirty_days).count()

    ytd = timezone.now().replace(month=1, day=1)
    transactions_ytd = Transaction.objects.filter(
        datePurchased__gte=ytd).count()

    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_ids = []
    for session in active_sessions:
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        if user_id and user_id not in user_ids:
            user_ids.append(user_id)

    active_user_count = User.objects.filter(id__in=user_ids).count() - 1

    customer_group = Group.objects.get(name='customer')
    total_user_count = customer_group.user_set.count()

    stocks = Stock.objects.all()
    stock_quantity = Stock.objects.count()
    for stock in stocks:
        stock.generateRandCost()

    message_quantity = ContactMessage.objects.count()
    unread_message_quantity = ContactMessage.objects.filter(read=False).count()

    context = {'transactions_today': transactions_today,
               'transactions_last_30_days': transactions_last_30_days,
               'transactions_ytd': transactions_ytd,
               'total_user_count': total_user_count,
               'active_user_count': active_user_count,
               'stocks': stocks,
               'stock_quantity': stock_quantity,
               'message_quantity': message_quantity,
               'unread_message_quantity': unread_message_quantity,
               }

    return render(request, 'adminpanel.html', context)


@allowed_users(allowed_roles=['admin'])
def markethours(request):
    market_hours, created = MarketHours.objects.get_or_create(
        defaults={'openTime': time(9, 0), 'closeTime': time(17, 0)}
    )

    hourform = MarketHoursForm(instance=market_hours)

    if request.method == 'POST':
        hourform = MarketHoursForm(request.POST, instance=market_hours)
        if hourform.is_valid():
            hourform.save()
            messages.success(request, 'Market Hours were updated')
        else:
            messages.error(request, 'Invalid Input for adding hours')

    else:
        hourform = MarketHoursForm(instance=market_hours)

    context = {
        'hourform': hourform,
        'market_hours': market_hours,
    }

    return render(request, 'markethours.html', context)


@allowed_users(allowed_roles=['admin'])
def stockmodification(request):
    stocks = Stock.objects.all()
    for stock in stocks:
        stock.generateRandCost()

    print('adding stock')
    if request.method == 'POST':
        stockCreationForm = ModifyStockForm(request.POST)
        if stockCreationForm.is_valid():
            stockName = stockCreationForm.cleaned_data.get('stockName')
            ticker = stockCreationForm.cleaned_data.get('ticker')
            price = stockCreationForm.cleaned_data.get('price')
            maxPrice = price
            minPrice = price
            volumeQty = stockCreationForm.cleaned_data.get('volumeQty')
            remainingVol = volumeQty

            if Stock.objects.filter(ticker=ticker).exists():
                messages.error(request, 'This stock already exists.')

            else:
                newStock = Stock.objects.create(
                    stockName=stockName,
                    ticker=ticker,
                    price=price,
                    maxPrice=maxPrice,
                    minPrice=minPrice,
                    volumeQty=volumeQty,
                    remainingVol=remainingVol
                )
                newStock.save()
                messages.success(request, f'{newStock.stockName} was created')

        stockDeletionForm = StockDeletionForm(request.POST)
        if stockDeletionForm.is_valid():
            deleteStock = stockDeletionForm.cleaned_data.get('stock')

            currentlyheld = any(deleteStock.ticker in portfolio.purchased_stock()
                                for portfolio in Portfolio.objects.all())

            if currentlyheld:
                messages.error(
                    request, f"Stock {deleteStock.stockName} cannot be deleted as it is currently held by a user.")
            else:
                deleteStock.delete()
                messages.success(
                    request, f'Stock {deleteStock.stockName} was deleted successfully')

        stockPriceAdjustmentForm = StockPriceAdjustmentForm(request.POST)
        if stockPriceAdjustmentForm.is_valid():
            updateStock = stockPriceAdjustmentForm.cleaned_data.get('stock')
            updatePrice = stockPriceAdjustmentForm.cleaned_data.get('price')
            updateStock.price = updatePrice
            updateStock.save()
            messages.success(
                request, f"Stock {updateStock.stockName}'s price updated")

    else:
        stockCreationForm = ModifyStockForm()
        stockDeletionForm = StockDeletionForm()
        stockPriceAdjustmentForm = StockPriceAdjustmentForm()

    context = {
        'stockCreationForm': stockCreationForm,
        'stockDeletionForm': stockDeletionForm,
        'stockPriceAdjustmentForm': stockPriceAdjustmentForm
    }

    return render(request, 'stockmodification.html', context)


@allowed_users(allowed_roles=['admin'])
def messagespanel(request):
    messages = ContactMessage.objects.all()
    paginator = Paginator(messages, 12)  # Show 12 messages per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'messagespanel.html', context)


@allowed_users(allowed_roles=['admin'])
def viewmessage(request, id):
    message = get_object_or_404(ContactMessage, id=id)
    message.read = True
    message.save()
    context = {'message': message}
    return render(request, 'viewmessage.html', context)


@allowed_users(allowed_roles=['admin'])
def deletemessage(request, id):
    message = get_object_or_404(ContactMessage, id=id)

    if request.method == "POST":
        message.delete()
        messages.success(request, "Message deleted successfully.")
        return redirect('messagespanel')

    return redirect('viewmessage', id=id)


@allowed_users(allowed_roles=['admin'])
def marketdays(request):
    market_days = MarketDay.objects.all()

    if request.method == 'POST':
        for day in market_days:
            day.status = request.POST.get(f'day{day.id}') == 'on'
            day.save()

        messages.success(request, 'Market Days were updated')

    context = {
        'market_days': market_days,
    }

    return render(request, 'marketdays.html', context)


@allowed_users(allowed_roles=['admin'])
def marketholidays(request):
    holidays = Holidays.objects.all()

    if request.method == 'POST':
        holidayForm = HolidaysForm(request.POST)
        if holidayForm.is_valid():
            holiday_date = holidayForm.cleaned_data['date']
            description = holidayForm.cleaned_data['description']

            if Holidays.objects.filter(date=holiday_date).exists():
                messages.error(request, 'Holiday on this date already exists.')
            else:
                new_holiday = Holidays(
                    date=holiday_date, description=description)
                new_holiday.save()
                messages.success(request, 'Holiday was added')
                return redirect('adminpanel')

        deleteholidayform = HolidaysDeletionForm(request.POST)
        if deleteholidayform.is_valid():
            deleteholiday = deleteholidayform.cleaned_data.get('holidays')

    else:
        holidayForm = HolidaysForm()
        deleteholidayform = HolidaysDeletionForm()

    # CALENDAR
    now = datetime.now()
    year = request.GET.get('year', now.year)
    month = request.GET.get('month', now.month)

    year = int(year)
    month = int(month)

    holidays_in_month = Holidays.objects.filter(
        date__year=year, date__month=month)

    cal = calendar.HTMLCalendar(calendar.SUNDAY)

    def formatday(day, weekday):
        if day == 0:
            return '<td></td>'

        holiday_for_day = next(
            (h for h in holidays_in_month if h.date.day == day), None)
        if holiday_for_day:
            return f'<td style="background-color: #ffcccc;">{day}<br><small>{holiday_for_day.description}</small></td>'
        return f'<td>{day}</td>'

    def formatmonth(year, month, withyear=True):
        cal_str = '<table border="0" cellpadding="0" cellspacing="0" class="month">\n'
        cal_str += f'{cal.formatmonthname(year, month, withyear=withyear)}\n'
        cal_str += f'{cal.formatweekheader()}\n'
        for week in cal.monthdayscalendar(year, month):
            cal_str += '<tr>'
            for day in week:
                cal_str += formatday(day, calendar.weekday(year,
                                     month, day) if day != 0 else None)
            cal_str += '</tr>\n'
        return cal_str + '</table>\n'

    html_calendar = formatmonth(year, month)

    previous_month = month - 1 if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        'html_calendar': html_calendar,
        'current_year': year,
        'current_month': month,
        'previous_year': previous_year,
        'previous_month': previous_month,
        'next_year': next_year,
        'next_month': next_month,
        'holidayForm': holidayForm,
        'holidays': holidays,
        'deleteholidayform': deleteholidayform,
    }

    return render(request, 'marketholidays.html', context)
