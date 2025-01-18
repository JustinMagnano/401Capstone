from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('market/', views.market, name='market'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutPage, name='logout'),
    # user pages
    path('userpanel/', views.userPanel, name='userpanel'),
    path('funds/', views.funds, name='funds'),
    path('transactions/', views.transactions, name='transactions'),
    path('stockmarket/', views.stockmarket, name='stockmarket'),
    path('market/stockmarket.html/', views.stockmarket, name='stockmarket'),
    # admin pages
    path('adminpanel/', views.adminPanel, name='adminpanel'),
    path("stockmodification/", views.stockmodification, name="stockmodification"),
    path('markethours/', views.markethours, name='markethours'),
    path('marketdays/', views.marketdays, name='marketdays'),
    path('marketholidays/', views.marketholidays, name='marketholidays'),
    path('messagespanel/', views.messagespanel, name='messagespanel'),
    path('viewmessage/<int:id>/', views.viewmessage, name='viewmessage'),
    path('deletemessage/<int:id>/', views.deletemessage, name='deletemessage'),

]
