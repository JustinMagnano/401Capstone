from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('market/', views.market, name='market'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutPage, name='logout'),
    ##user pages
    path('userpanel/', views.userPanel, name='userpanel'),
    path('funds/', views.funds, name='funds'),
    path('transactions/', views.transactions, name='transactions'),
    path('stockmarket/', views.stockmarket, name='stockmarket'),
    path('market/stockmarket.html/', views.stockmarket, name='stockmarket'),
    ##admin pages
    path('adminpanel/', views.adminPanel, name='adminpanel'),
    path('stockcreation/', views.stockcreation, name='stockcreation'),
    path('stockdeletion/', views.stockdeletion, name='stockdeletion'),
    path('markethours/', views.markethours, name='markethours'),
    
]