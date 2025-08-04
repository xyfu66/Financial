"""
Management command to set up the financial system
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.business.models import IncomeCategory, ExpenseCategory
from apps.system.models import SystemConfiguration, Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up the financial system with initial data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Superuser username (default: admin)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@financialsystem.com',
            help='Superuser email',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Superuser password (default: admin123)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up Financial System...')
        )
        
        with transaction.atomic():
            # Create default categories
            self.create_default_categories()
            
            # Create system configurations
            self.create_system_configurations()
            
            # Create welcome notification
            self.create_welcome_notification()
            
            # Create superuser if requested
            if options['create_superuser']:
                self.create_superuser(
                    options['username'],
                    options['email'],
                    options['password']
                )
        
        self.stdout.write(
            self.style.SUCCESS('Financial System setup completed successfully!')
        )
    
    def create_default_categories(self):
        """Create default income and expense categories"""
        self.stdout.write('Creating default categories...')
        
        # Default income categories
        income_categories = [
            {
                'name': '事業収入',
                'code': 'BUS001',
                'category_type': 'business',
                'description': '事業による収入',
                'is_taxable': True,
                'blue_tax_deduction_eligible': True
            },
            {
                'name': '給与収入',
                'code': 'SAL001',
                'category_type': 'salary',
                'description': '給与・賞与による収入',
                'is_taxable': True,
                'blue_tax_deduction_eligible': False
            },
            {
                'name': '年金収入',
                'code': 'PEN001',
                'category_type': 'pension',
                'description': '年金による収入',
                'is_taxable': True,
                'blue_tax_deduction_eligible': False
            },
            {
                'name': '投資収入',
                'code': 'INV001',
                'category_type': 'investment',
                'description': '投資による収入',
                'is_taxable': True,
                'blue_tax_deduction_eligible': False
            },
            {
                'name': '不動産収入',
                'code': 'REA001',
                'category_type': 'rental',
                'description': '不動産による収入',
                'is_taxable': True,
                'blue_tax_deduction_eligible': True
            },
            {
                'name': 'その他収入',
                'code': 'OTH001',
                'category_type': 'other',
                'description': 'その他の収入',
                'is_taxable': True,
                'blue_tax_deduction_eligible': False
            }
        ]
        
        for cat_data in income_categories:
            category, created = IncomeCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  Created income category: {category.name}')
        
        # Default expense categories
        expense_categories = [
            {
                'name': '消耗品費',
                'code': 'SUP001',
                'category_type': 'supplies',
                'description': '事務用品、消耗品等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '通信費',
                'code': 'COM001',
                'category_type': 'communication',
                'description': '電話代、インターネット代等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '旅費交通費',
                'code': 'TRA001',
                'category_type': 'travel',
                'description': '出張費、交通費等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '接待交際費',
                'code': 'ENT001',
                'category_type': 'entertainment',
                'description': '接待費、交際費等',
                'is_deductible': True,
                'deduction_rate': 50.0,  # 50% deductible
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '地代家賃',
                'code': 'REN001',
                'category_type': 'rent',
                'description': '事務所家賃、駐車場代等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '水道光熱費',
                'code': 'UTI001',
                'category_type': 'utilities',
                'description': '電気代、ガス代、水道代等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '広告宣伝費',
                'code': 'ADV001',
                'category_type': 'advertising',
                'description': '広告費、宣伝費等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '保険料',
                'code': 'INS001',
                'category_type': 'insurance',
                'description': '事業用保険料',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '修繕費',
                'code': 'REP001',
                'category_type': 'repairs',
                'description': '設備修繕費等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '減価償却費',
                'code': 'DEP001',
                'category_type': 'depreciation',
                'description': '固定資産の減価償却',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': False
            },
            {
                'name': '租税公課',
                'code': 'TAX001',
                'category_type': 'taxes',
                'description': '事業税、固定資産税等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '支払手数料',
                'code': 'FEE001',
                'category_type': 'professional_fees',
                'description': '専門家報酬、手数料等',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            },
            {
                'name': '雑費',
                'code': 'MIS001',
                'category_type': 'miscellaneous',
                'description': 'その他の経費',
                'is_deductible': True,
                'blue_tax_deduction_eligible': True,
                'requires_receipt': True
            }
        ]
        
        for cat_data in expense_categories:
            category, created = ExpenseCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  Created expense category: {category.name}')
    
    def create_system_configurations(self):
        """Create default system configurations"""
        self.stdout.write('Creating system configurations...')
        
        configs = [
            {
                'key': 'SYSTEM_NAME',
                'value': '個人財務管理システム',
                'value_type': 'STRING',
                'description': 'システム名',
                'category': 'system'
            },
            {
                'key': 'SYSTEM_VERSION',
                'value': '1.0.0',
                'value_type': 'STRING',
                'description': 'システムバージョン',
                'category': 'system'
            },
            {
                'key': 'DEFAULT_TAX_RATE',
                'value': '10.0',
                'value_type': 'FLOAT',
                'description': 'デフォルト消費税率（%）',
                'category': 'tax'
            },
            {
                'key': 'BLUE_TAX_DEDUCTION_AMOUNT',
                'value': '650000',
                'value_type': 'INTEGER',
                'description': '青色申告特別控除額（円）',
                'category': 'tax'
            },
            {
                'key': 'MAX_FILE_SIZE_MB',
                'value': '10',
                'value_type': 'INTEGER',
                'description': '最大ファイルサイズ（MB）',
                'category': 'file'
            },
            {
                'key': 'NOTIFICATION_RETENTION_DAYS',
                'value': '30',
                'value_type': 'INTEGER',
                'description': '通知保持日数',
                'category': 'notification'
            },
            {
                'key': 'AUDIT_LOG_RETENTION_DAYS',
                'value': '365',
                'value_type': 'INTEGER',
                'description': '監査ログ保持日数',
                'category': 'audit'
            },
            {
                'key': 'BACKUP_RETENTION_DAYS',
                'value': '30',
                'value_type': 'INTEGER',
                'description': 'バックアップ保持日数',
                'category': 'backup'
            }
        ]
        
        for config_data in configs:
            config, created = SystemConfiguration.objects.get_or_create(
                key=config_data['key'],
                defaults=config_data
            )
            if created:
                self.stdout.write(f'  Created configuration: {config.key}')
    
    def create_welcome_notification(self):
        """Create welcome notification"""
        self.stdout.write('Creating welcome notification...')
        
        notification, created = Notification.objects.get_or_create(
            title='システムへようこそ',
            defaults={
                'message': '''個人財務管理システムへようこそ！

このシステムでは以下の機能をご利用いただけます：
• 収入・支出の記録と管理
• レシート・請求書のOCR処理
• 税務計算と青色申告対応
• データのインポート・エクスポート
• 詳細な財務レポート

ご不明な点がございましたら、管理者までお問い合わせください。''',
                'notification_type': 'INFO',
                'priority': 'NORMAL',
                'is_global': True,
                'show_on_login': True,
                'show_on_dashboard': True,
                'is_dismissible': True
            }
        )
        
        if created:
            self.stdout.write('  Created welcome notification')
    
    def create_superuser(self, username, email, password):
        """Create superuser account"""
        self.stdout.write(f'Creating superuser: {username}...')
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser {username} already exists')
            )
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Create user detail
        from apps.users.models import UserDetail
        UserDetail.objects.create(
            user=user,
            first_name='管理者',
            last_name='システム',
            occupation='システム管理者',
            occupation_category='other',
            primary_income_source='other'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Superuser {username} created successfully')
        )
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(
            self.style.WARNING('Please change the password after first login!')
        )