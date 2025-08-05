# Personal Financial Management System - Setup Guide

## システム概要 (System Overview)

個人事業主向けの包括的な財務管理システムです。OCR機能による領収書読み取り、自動計算、PDF レポート生成機能を提供します。

A comprehensive financial management system for Japanese individual business owners with OCR capabilities, automatic calculations, and PDF reporting.

## 技術スタック (Technology Stack)

### Backend
- **Python 3.10** - Django RESTful API
- **PostgreSQL 14+** - Database
- **JWT Authentication** - Security
- **Claude API** - OCR Processing

### Frontend
- **Vue.js 3.5.18** - Frontend Framework
- **Element Plus** - UI Components
- **Pinia** - State Management
- **Vue Router 4** - Routing
- **Vue I18n** - Internationalization

## 前提条件 (Prerequisites)

### Development Environment
- **Node.js** >= 18.0.0
- **Python** >= 3.10
- **PostgreSQL** >= 14.0
- **Git**
- **Windows 11**

### Production Environment
- **Linux Server** (Ubuntu 20.04+ 推奨) または **Windows Server** 2019/2022
- **PostgreSQL** >= 14.0
- **Nginx** (リバースプロキシ用)
- **4GB RAM** minimum (8GB recommended)
- **20GB** disk space minimum

## 開発環境セットアップ (Development Setup)

### 1. リポジトリのクローン (Clone Repository)
```bash
git clone <repository-url>
cd FinancialSystem/Financial
```

### 2. PostgreSQL セットアップ (PostgreSQL Setup)

#### PostgreSQL のインストール
1. **PostgreSQL 14+** をダウンロード・インストール
2. **pgAdmin** または **psql** クライアントをインストール
3. PostgreSQL サービスを起動し、接続を確認

#### データベース作成
1. PostgreSQL に接続し、データベースを作成：
   ```sql
   CREATE DATABASE financial_system;
   ```
2. 以下のスクリプトを順番に実行：
   ```bash
   # 1. データベーススキーマ作成
   psql -d financial_system -f database/create_database.sql
   
   # 2. ビジネステーブル作成
   psql -d financial_system -f database/create_business_tables.sql
   
   # 3. 初期データ投入
   psql -d financial_system -f database/initial_data.sql
   ```

### 3. バックエンドセットアップ (Backend Setup)
```bash
cd backend

# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
```

#### .env ファイル設定
```env
# Django Configuration
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://postgres:your-strong-password@localhost:5432/financial_system
DB_NAME=financial_system
DB_USER=postgres
DB_PASSWORD=your-strong-password
DB_HOST=localhost
DB_PORT=5432

# Claude API Configuration
CLAUDE_API_KEY=your-claude-api-key

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Upload Configuration
MAX_UPLOAD_SIZE=10485760  # 10MB
MEDIA_ROOT=media/
STATIC_ROOT=staticfiles/
```

#### Django プロジェクト初期化 (注意: 手動実行が必要)
以下のコマンドは手動で実行してください：

```bash
# Django プロジェクト作成 (backend/ ディレクトリ内で実行)
django-admin startproject financial_system .

# Django アプリケーション作成
python manage.py startapp accounts
python manage.py startapp financial
python manage.py startapp notifications
python manage.py startapp audit
python manage.py startapp ocr_service

# データベースマイグレーション
python manage.py makemigrations
python manage.py migrate

# 管理者ユーザー作成
python manage.py createsuperuser

# 開発サーバー起動
python manage.py runserver
```

### 4. フロントエンドセットアップ (Frontend Setup)
```bash
cd frontend

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

### 5. アクセス確認 (Access Verification)
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/

## 本番環境デプロイ (Production Deployment)

### Windows Server での展開

#### 1. 環境準備
```bash
# Ubuntu/Debian の場合
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip nodejs npm postgresql postgresql-contrib nginx

# CentOS/RHEL の場合
sudo yum install python3.10 nodejs npm postgresql-server postgresql-contrib nginx
```

#### 2. アプリケーション配置
```bash
# プロジェクトファイルをサーバーにコピー
# 例: C:\inetpub\FinancialSystem\

# バックエンド設定
cd C:\inetpub\FinancialSystem\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# フロントエンドビルド
cd C:\inetpub\FinancialSystem\frontend
npm install
npm run build
```

#### 3. Windows Service として実行 (推奨)
```bash
# NSSM (Non-Sucking Service Manager) を使用
# https://nssm.cc/ からダウンロード

# バックエンドサービス作成
nssm install FinancialBackend
nssm set FinancialBackend Application C:\inetpub\FinancialSystem\backend\venv\Scripts\python.exe
nssm set FinancialBackend AppParameters C:\inetpub\FinancialSystem\backend\main.py
nssm set FinancialBackend AppDirectory C:\inetpub\FinancialSystem\backend
nssm start FinancialBackend
```

#### 4. IIS 設定 (フロントエンド)
1. IIS Manager を開く
2. 新しいサイトを作成
3. 物理パス: `C:\inetpub\FinancialSystem\frontend\dist`
4. バインディング: ポート 80 (または 443 for HTTPS)
5. URL Rewrite モジュールをインストール
6. web.config を作成:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Handle History Mode and Hash Mode" stopProcessing="true">
          <match url="(.*)" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
    <staticContent>
      <mimeMap fileExtension=".json" mimeType="application/json" />
    </staticContent>
  </system.webServer>
</configuration>
```

## 初期ユーザー作成 (Initial User Creation)

### 管理者ユーザー作成スクリプト
```python
# create_admin.py
from app.models.user import User, UserDetail
from app.core.database import SessionLocal
from app.core.security import get_password_hash

def create_admin_user():
    db = SessionLocal()
    
    try:
        # 管理者ユーザー作成
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=get_password_hash('admin123'),
            role='super_admin',
            is_active=True
        )
        
        db.add(admin_user)
        db.flush()
        
        # ユーザー詳細作成
        user_detail = UserDetail(
            user_id=admin_user.user_id,
            first_name='管理者',
            last_name='システム'
        )
        
        db.add(user_detail)
        db.commit()
        print('Admin user created successfully')
        print(f'Username: admin')
        print(f'Password: admin123')
        
    except Exception as e:
        db.rollback()
        print(f'Error creating admin user: {e}')
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
```

実行:
```bash
cd backend
python create_admin.py
```

## メンテナンス (Maintenance)

### バックアップ
```bash
# PostgreSQL データベースバックアップ
pg_dump -h localhost -U postgres -d financial_system > backup_$(date +%Y%m%d).sql

# 復元
psql -h localhost -U postgres -d financial_system < backup_20231201.sql
```

### ログ監視
```bash
# バックエンドログ
tail -f backend/logs/app.log

# Windows イベントログも確認
```

### アップデート手順
```bash
# 1. サービス停止
net stop FinancialBackend

# 2. コードアップデート
git pull origin main

# 3. 依存関係更新
cd backend
pip install -r requirements.txt

cd frontend
npm install
npm run build

# 4. サービス再開
net start FinancialBackend
```

## トラブルシューティング (Troubleshooting)

### よくある問題 (Common Issues)

1. **データベース接続エラー**
   ```bash
   # PostgreSQL サービス確認
   sudo systemctl status postgresql
   
   # 接続テスト
   psql -h localhost -U postgres -d financial_system
   ```

2. **Python 依存関係エラー**
   ```bash
   # 仮想環境の再作成
   rm -rf venv
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **フロントエンドビルドエラー**
   ```bash
   # Node modules 再インストール
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

4. **ポート競合エラー**
   ```bash
   # ポート使用状況確認
   sudo netstat -tlnp | grep :8000
   sudo netstat -tlnp | grep :5173
   ```

### ログ確認方法
```bash
# Backend ログ
type backend\logs\app.log

# Windows イベントログ
eventvwr.msc
```

## セキュリティ考慮事項 (Security Considerations)

1. **本番環境では必ず強力なパスワードを使用**
2. **HTTPS を有効にする**
3. **Windows Firewall の設定**
4. **定期的なセキュリティアップデート**
5. **データベースの定期バックアップ**
6. **アクセスログの監視**

## パフォーマンス最適化 (Performance Optimization)

### PostgreSQL 設定
```sql
-- 統計情報更新
ANALYZE T_Dat_Incomes;
ANALYZE T_Dat_Expenses;

-- インデックス再構築
REINDEX TABLE T_Dat_Incomes;
REINDEX TABLE T_Dat_Expenses;
```

### IIS 設定
- **静的ファイル圧縮** を有効化
- **キャッシュ設定** を最適化
- **接続プール** を調整

## サポート (Support)

技術的な問題や質問がある場合は、以下の情報を含めてお問い合わせください：

- エラーメッセージ
- 実行環境（OS、ブラウザなど）
- 再現手順
- ログファイル

---

**注意**: このシステムは個人事業主の財務管理を目的として設計されています。税務申告等の重要な用途で使用する前に、税理士等の専門家にご相談ください。