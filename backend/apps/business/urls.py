"""
URL configuration for business app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IncomeCategoryViewSet, ExpenseCategoryViewSet, IncomeViewSet,
    ExpenseViewSet, TaxCalculationViewSet, FinancialSummaryView
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'income-categories', IncomeCategoryViewSet, basename='incomecategory')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expensecategory')
router.register(r'incomes', IncomeViewSet, basename='income')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'tax-calculations', TaxCalculationViewSet, basename='taxcalculation')

app_name = 'business'

urlpatterns = [
    # Financial summary endpoint
    path('summary/', FinancialSummaryView.as_view(), name='financial-summary'),
    
    # Router URLs
    path('', include(router.urls)),
]