# Personal Financial Management System - Setup Guide

## システム概要 (System Overview)

個人事業主向けの包括的な財務管理システムです。OCR機能による領収書読み取り、自動計算、PDF レポート生成機能を提供します。

A comprehensive financial management system for Japanese individual business owners with OCR capabilities, automatic calculations, and PDF reporting.

## 技術スタック (Technology Stack)

### Backend
- **Python 3.10** - FastAPI RESTful API
- **SQL Server 2019** - Database
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
- **SQL Server 2019** (Express Edition可)
- **Git**

### Production Environment
- **Windows Server** 2019/2022 (推奨)
- **SQL Server 2019**
- **IIS** または **Nginx** (リバースプロキシ用)
- **4GB RAM** minimum (8GB recommended)
- **20GB** disk space minimum

## 開発環境セットアップ (Development Setup)

### 1. リポジトリのクローン (Clone Repository)
```bash
git clone <repository-url>
cd FinancialSystem/Financial
```

### 2. SQL Server セットアップ (SQL Server Setup)

#### SQL Server のインストール
1. **SQL Server 2019 Express** をダウンロード・インストール
2. **SQL Server Management Studio (SSMS)** をインストール
3. SQL Server を起動し、接続を確認

#### データベース作成
1. SSMS を開き、SQL Server に接続
2. 以下のスクリプトを順番に実行：
   ```sql
   -- 1. データベース作成
   -- database/create_database.sql を実行
   
   -- 2. ビジネステーブル作成
   -- database/create_business_tables.sql を実行
   
   -- 3. 初期データ投入
   -- database/initial_data.sql を実行
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
# Database Configuration
DB_SERVER=localhost
DB_NAME=FinancialManagement
DB_USER=sa
DB_PASSWORD=your-strong-password

# Security Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Claude API Configuration
CLAUDE_API_KEY=your-claude-api-key

# Application Configuration
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8100
```

#### アプリケーション起動
```bash
python main.py
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
- **Frontend**: http://localhost:3100
- **Backend API**: http://localhost:8100
- **API Documentation**: http://localhost:8100/api/docs

## 本番環境デプロイ (Production Deployment)

### Windows Server での展開

#### 1. 環境準備
```powershell
# Python 3.10 インストール
# Node.js 18+ インストール
# SQL Server 2019 インストール
# IIS インストール (オプション)
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
```sql
-- データベースバックアップ
BACKUP DATABASE FinancialManagement 
TO DISK = 'C:\Backup\FinancialManagement_backup.bak'
WITH FORMAT, INIT;
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
   # SQL Server サービス確認
   services.msc で SQL Server サービスを確認
   
   # 接続テスト
   sqlcmd -S localhost -U sa -P your-password
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
   netstat -ano | findstr :8100
   netstat -ano | findstr :3100
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

### SQL Server 設定
```sql
-- インデックス最適化
EXEC sp_updatestats;

-- 統計情報更新
UPDATE STATISTICS T_Dat_Incomes;
UPDATE STATISTICS T_Dat_Expenses;
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