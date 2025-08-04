"""
Views for Business models
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from decimal import Decimal
from datetime import datetime, date
import pandas as pd
import io

from .models import IncomeCategory, ExpenseCategory, Income, Expense, TaxCalculation
from .serializers import (
    IncomeCategorySerializer, ExpenseCategorySerializer,
    IncomeSerializer, IncomeCreateSerializer, IncomeUpdateSerializer, IncomeListSerializer,
    ExpenseSerializer, ExpenseCreateSerializer, ExpenseUpdateSerializer, ExpenseListSerializer,
    TaxCalculationSerializer, FinancialSummarySerializer, BulkImportSerializer
)
from .filters import IncomeCategoryFilter, ExpenseCategoryFilter, IncomeFilter, ExpenseFilter
from apps.users.permissions import IsAdminOrOwner, CanViewIncomes, CanCreateIncomes, CanEditIncomes, CanDeleteIncomes


class IncomeCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for IncomeCategory model
    """
    queryset = IncomeCategory.objects.all()
    serializer_class = IncomeCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = IncomeCategoryFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['code']
    
    def get_queryset(self):
        """
        Filter active categories for regular users
        """
        queryset = self.queryset
        if not self.request.user.is_admin:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    def perform_create(self, serializer):
        """
        Create category with created_by field
        """
        serializer.save(created_by=self.request.user)


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ExpenseCategory model
    """
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ExpenseCategoryFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['code']
    
    def get_queryset(self):
        """
        Filter active categories for regular users
        """
        queryset = self.queryset
        if not self.request.user.is_admin:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    def perform_create(self, serializer):
        """
        Create category with created_by field
        """
        serializer.save(created_by=self.request.user)


class IncomeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Income model
    """
    queryset = Income.objects.all().select_related('category', 'user', 'created_by', 'updated_by')
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = IncomeFilter
    search_fields = ['description', 'client_name', 'invoice_number']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return IncomeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IncomeUpdateSerializer
        elif self.action == 'list':
            return IncomeListSerializer
        return IncomeSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        else:
            # Regular users can only see their own incomes
            return self.queryset.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Create income with audit logging
        """
        with transaction.atomic():
            income = serializer.save()
            # Log income creation in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='CREATE',
                model='Income',
                object_id=income.id,
                changes={'created': True}
            )
    
    def perform_update(self, serializer):
        """
        Update income with audit logging
        """
        old_instance = self.get_object()
        old_data = IncomeSerializer(old_instance).data
        
        with transaction.atomic():
            income = serializer.save()
            new_data = IncomeSerializer(income).data
            
            # Log income update in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='UPDATE',
                model='Income',
                object_id=income.id,
                old_values=old_data,
                new_values=new_data
            )
    
    def perform_destroy(self, instance):
        """
        Delete income with audit logging
        """
        with transaction.atomic():
            # Log income deletion in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='DELETE',
                model='Income',
                object_id=instance.id,
                changes={'deleted': True}
            )
            instance.delete()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get income summary for current user
        """
        user = request.user
        queryset = self.get_queryset()
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Calculate totals
        totals = queryset.aggregate(
            total_amount=Sum('amount'),
            total_tax=Sum('tax_amount'),
            count=Count('id')
        )
        
        # Get category breakdown
        category_breakdown = queryset.values(
            'category__name', 'category__code'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Get monthly breakdown
        monthly_breakdown = queryset.extra(
            select={'month': "strftime('%%Y-%%m', date)"}
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        return Response({
            'totals': totals,
            'category_breakdown': category_breakdown,
            'monthly_breakdown': monthly_breakdown
        })
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """
        Bulk import incomes from CSV/Excel file
        """
        serializer = BulkImportSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            skip_duplicates = serializer.validated_data['skip_duplicates']
            validate_only = serializer.validated_data['validate_only']
            
            try:
                # Read file based on extension
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Process import
                results = self._process_income_import(df, skip_duplicates, validate_only)
                
                return Response(results)
                
            except Exception as e:
                return Response(
                    {'error': f'Failed to process file: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_income_import(self, df, skip_duplicates, validate_only):
        """
        Process income import from DataFrame
        """
        results = {
            'total_rows': len(df),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        for index, row in df.iterrows():
            try:
                # Map DataFrame columns to model fields
                income_data = {
                    'date': pd.to_datetime(row.get('date', '')).date(),
                    'amount': Decimal(str(row.get('amount', 0))),
                    'description': row.get('description', ''),
                    'client_name': row.get('client_name', ''),
                    'payment_method': row.get('payment_method', 'cash'),
                    'tax_rate': Decimal(str(row.get('tax_rate', 10))),
                    'is_tax_inclusive': row.get('is_tax_inclusive', True),
                    'status': row.get('status', 'pending'),
                }
                
                # Get or create category
                category_code = row.get('category_code', '')
                if category_code:
                    try:
                        category = IncomeCategory.objects.get(code=category_code, is_active=True)
                        income_data['category'] = category
                    except IncomeCategory.DoesNotExist:
                        results['errors'].append(f"Row {index + 1}: Category '{category_code}' not found")
                        results['failed'] += 1
                        continue
                
                # Check for duplicates if skip_duplicates is True
                if skip_duplicates:
                    existing = Income.objects.filter(
                        user=self.request.user,
                        date=income_data['date'],
                        amount=income_data['amount'],
                        description=income_data['description']
                    ).exists()
                    
                    if existing:
                        results['skipped'] += 1
                        continue
                
                # Validate data
                serializer = IncomeCreateSerializer(
                    data=income_data,
                    context={'request': self.request}
                )
                
                if serializer.is_valid():
                    if not validate_only:
                        serializer.save()
                    results['successful'] += 1
                else:
                    results['errors'].append(f"Row {index + 1}: {serializer.errors}")
                    results['failed'] += 1
                    
            except Exception as e:
                results['errors'].append(f"Row {index + 1}: {str(e)}")
                results['failed'] += 1
        
        return results


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Expense model
    """
    queryset = Expense.objects.all().select_related('category', 'user', 'created_by', 'updated_by')
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ExpenseFilter
    search_fields = ['description', 'vendor_name', 'receipt_number']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return ExpenseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ExpenseUpdateSerializer
        elif self.action == 'list':
            return ExpenseListSerializer
        return ExpenseSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        else:
            # Regular users can only see their own expenses
            return self.queryset.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Create expense with audit logging
        """
        with transaction.atomic():
            expense = serializer.save()
            # Log expense creation in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='CREATE',
                model='Expense',
                object_id=expense.id,
                changes={'created': True}
            )
    
    def perform_update(self, serializer):
        """
        Update expense with audit logging
        """
        old_instance = self.get_object()
        old_data = ExpenseSerializer(old_instance).data
        
        with transaction.atomic():
            expense = serializer.save()
            new_data = ExpenseSerializer(expense).data
            
            # Log expense update in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='UPDATE',
                model='Expense',
                object_id=expense.id,
                old_values=old_data,
                new_values=new_data
            )
    
    def perform_destroy(self, instance):
        """
        Delete expense with audit logging
        """
        with transaction.atomic():
            # Log expense deletion in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='DELETE',
                model='Expense',
                object_id=instance.id,
                changes={'deleted': True}
            )
            instance.delete()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get expense summary for current user
        """
        user = request.user
        queryset = self.get_queryset()
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Calculate totals
        totals = queryset.aggregate(
            total_amount=Sum('amount'),
            total_tax=Sum('tax_amount'),
            total_deductible=Sum('business_deductible_amount'),
            count=Count('id')
        )
        
        # Get category breakdown
        category_breakdown = queryset.values(
            'category__name', 'category__code'
        ).annotate(
            total=Sum('amount'),
            deductible=Sum('business_deductible_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Get monthly breakdown
        monthly_breakdown = queryset.extra(
            select={'month': "strftime('%%Y-%%m', date)"}
        ).values('month').annotate(
            total=Sum('amount'),
            deductible=Sum('business_deductible_amount'),
            count=Count('id')
        ).order_by('month')
        
        return Response({
            'totals': totals,
            'category_breakdown': category_breakdown,
            'monthly_breakdown': monthly_breakdown
        })
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """
        Bulk import expenses from CSV/Excel file
        """
        serializer = BulkImportSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            skip_duplicates = serializer.validated_data['skip_duplicates']
            validate_only = serializer.validated_data['validate_only']
            
            try:
                # Read file based on extension
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Process import
                results = self._process_expense_import(df, skip_duplicates, validate_only)
                
                return Response(results)
                
            except Exception as e:
                return Response(
                    {'error': f'Failed to process file: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_expense_import(self, df, skip_duplicates, validate_only):
        """
        Process expense import from DataFrame
        """
        results = {
            'total_rows': len(df),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        for index, row in df.iterrows():
            try:
                # Map DataFrame columns to model fields
                expense_data = {
                    'date': pd.to_datetime(row.get('date', '')).date(),
                    'amount': Decimal(str(row.get('amount', 0))),
                    'description': row.get('description', ''),
                    'vendor_name': row.get('vendor_name', ''),
                    'payment_method': row.get('payment_method', 'cash'),
                    'tax_rate': Decimal(str(row.get('tax_rate', 10))),
                    'is_tax_inclusive': row.get('is_tax_inclusive', True),
                    'business_use_percentage': Decimal(str(row.get('business_use_percentage', 100))),
                    'status': row.get('status', 'pending'),
                }
                
                # Get or create category
                category_code = row.get('category_code', '')
                if category_code:
                    try:
                        category = ExpenseCategory.objects.get(code=category_code, is_active=True)
                        expense_data['category'] = category
                    except ExpenseCategory.DoesNotExist:
                        results['errors'].append(f"Row {index + 1}: Category '{category_code}' not found")
                        results['failed'] += 1
                        continue
                
                # Check for duplicates if skip_duplicates is True
                if skip_duplicates:
                    existing = Expense.objects.filter(
                        user=self.request.user,
                        date=expense_data['date'],
                        amount=expense_data['amount'],
                        description=expense_data['description']
                    ).exists()
                    
                    if existing:
                        results['skipped'] += 1
                        continue
                
                # Validate data
                serializer = ExpenseCreateSerializer(
                    data=expense_data,
                    context={'request': self.request}
                )
                
                if serializer.is_valid():
                    if not validate_only:
                        serializer.save()
                    results['successful'] += 1
                else:
                    results['errors'].append(f"Row {index + 1}: {serializer.errors}")
                    results['failed'] += 1
                    
            except Exception as e:
                results['errors'].append(f"Row {index + 1}: {str(e)}")
                results['failed'] += 1
        
        return results


class TaxCalculationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TaxCalculation model
    """
    queryset = TaxCalculation.objects.all().select_related('user', 'calculated_by')
    serializer_class = TaxCalculationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['calculation_type', 'tax_year']
    ordering_fields = ['tax_year', 'end_date', 'created_at']
    ordering = ['-tax_year', '-end_date']
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        else:
            # Regular users can only see their own calculations
            return self.queryset.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Create tax calculation with calculated_by field
        """
        serializer.save(calculated_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """
        Calculate tax for specified period
        """
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        calculation_type = request.data.get('calculation_type', 'monthly')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate tax for the period
        calculation_data = self._calculate_tax_for_period(
            request.user, start_date, end_date, calculation_type
        )
        
        return Response(calculation_data)
    
    def _calculate_tax_for_period(self, user, start_date, end_date, calculation_type):
        """
        Calculate tax for specified period
        """
        # Get incomes for the period
        incomes = Income.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date,
            status='confirmed'
        )
        
        # Get expenses for the period
        expenses = Expense.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date,
            status='confirmed'
        )
        
        # Calculate totals
        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        total_income_tax = incomes.aggregate(Sum('tax_amount'))['tax_amount__sum'] or Decimal('0')
        
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        total_expense_tax = expenses.aggregate(Sum('tax_amount'))['tax_amount__sum'] or Decimal('0')
        
        # Calculate business deductible expenses
        business_expenses = sum(
            expense.business_deductible_amount for expense in expenses
        )
        
        # Calculate net values
        net_income = total_income - business_expenses
        net_tax = total_income_tax - total_expense_tax
        
        # Calculate blue tax deduction (simplified)
        blue_tax_deduction = Decimal('0')
        if hasattr(user, 'detail') and user.detail.blue_tax_return_approved:
            # Blue tax deduction can be up to 650,000 yen for electronic filing
            blue_tax_deduction = min(net_income, Decimal('650000'))
        
        # Calculate taxable income
        taxable_income = max(net_income - blue_tax_deduction, Decimal('0'))
        
        return {
            'period_start': start_date,
            'period_end': end_date,
            'calculation_type': calculation_type,
            'total_income': total_income,
            'total_income_tax': total_income_tax,
            'total_expenses': total_expenses,
            'business_expenses': business_expenses,
            'total_expense_tax': total_expense_tax,
            'net_income': net_income,
            'net_tax': net_tax,
            'blue_tax_deduction': blue_tax_deduction,
            'taxable_income': taxable_income,
            'income_count': incomes.count(),
            'expense_count': expenses.count(),
        }


class FinancialSummaryView(APIView):
    """
    View for financial summary and dashboard data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get financial summary for current user
        """
        user = request.user
        
        # Get date range from query params (default to current year)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date:
            start_date = date(timezone.now().year, 1, 1)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = timezone.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get user's data
        if user.is_admin:
            incomes = Income.objects.filter(date__gte=start_date, date__lte=end_date)
            expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date)
        else:
            incomes = Income.objects.filter(user=user, date__gte=start_date, date__lte=end_date)
            expenses = Expense.objects.filter(user=user, date__gte=start_date, date__lte=end_date)
        
        # Calculate summary data
        summary_data = self._calculate_summary(incomes, expenses, start_date, end_date)
        
        serializer = FinancialSummarySerializer(summary_data)
        return Response(serializer.data)
    
    def _calculate_summary(self, incomes, expenses, start_date, end_date):
        """
        Calculate financial summary data
        """
        # Basic totals
        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        net_income = total_income - total_expenses
        
        total_income_tax = incomes.aggregate(Sum('tax_amount'))['tax_amount__sum'] or Decimal('0')
        total_expense_tax = expenses.aggregate(Sum('tax_amount'))['tax_amount__sum'] or Decimal('0')
        net_tax = total_income_tax - total_expense_tax
        
        # Category breakdowns
        income_by_category = {}
        for income in incomes.values('category__name').annotate(total=Sum('amount')):
            income_by_category[income['category__name']] = income['total']
        
        expenses_by_category = {}
        for expense in expenses.values('category__name').annotate(total=Sum('amount')):
            expenses_by_category[expense['category__name']] = expense['total']
        
        # Monthly data
        monthly_data = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_end = current_date.replace(
                month=current_date.month + 1 if current_date.month < 12 else 1,
                year=current_date.year + 1 if current_date.month == 12 else current_date.year,
                day=1
            ) - timezone.timedelta(days=1)
            
            month_incomes = incomes.filter(
                date__gte=current_date,
                date__lte=min(month_end, end_date)
            )
            month_expenses = expenses.filter(
                date__gte=current_date,
                date__lte=min(month_end, end_date)
            )
            
            month_income_total = month_incomes.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            month_expense_total = month_expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            
            monthly_data.append({
                'month': current_date.strftime('%Y-%m'),
                'income': month_income_total,
                'expenses': month_expense_total,
                'net': month_income_total - month_expense_total
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return {
            'period_start': start_date,
            'period_end': end_date,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_income': net_income,
            'total_income_tax': total_income_tax,
            'total_expense_tax': total_expense_tax,
            'net_tax': net_tax,
            'income_by_category': income_by_category,
            'expenses_by_category': expenses_by_category,
            'monthly_data': monthly_data
        }