# Veri-Train Backend クイックスタート

## 🚀 30秒で起動

```bash
# 1. 環境変数をコピー
cp .env.example .env

# 2. Dockerで全サービス起動
docker-compose up -d

# 3. データベース初期化
docker-compose exec api python scripts/init_db.py

# 4. 完了!
```

**アクセス先**:
- API Docs: http://localhost:8000/api/v1/docs
- Flower: http://localhost:5555

## 📝 動作確認

### 1. ヘルスチェック

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"Veri-Train API"}
```

### 2. API テスト

```bash
# モデル一覧取得
curl http://localhost:8000/api/v1/models

# データセット一覧
curl http://localhost:8000/api/v1/datasets

# 実験一覧
curl http://localhost:8000/api/v1/experiments
```

### 3. Celery タスクテスト

```bash
# Pythonコンテナに入る
docker-compose exec api python

# タスク実行
>>> from app.tasks.quality_gate import check_quality_gate
>>> task = check_quality_gate.delay("test-id")
>>> task.status
'SUCCESS'
```

## 🛠 ローカル開発

```bash
# 仮想環境作成
python3.11 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# DBとRedisのみDocker起動
docker-compose up -d postgres redis

# 環境変数設定
export DATABASE_URL=postgresql://veritrain:veritrain@localhost:5432/veritrain
export REDIS_URL=redis://localhost:6379/0

# DB初期化
python scripts/init_db.py

# FastAPI起動
uvicorn app.main:app --reload

# Celery起動(別ターミナル)
celery -A app.tasks.celery_app worker --loglevel=info
```

## 🔧 トラブルシューティング

### ポート衝突

```bash
# 使用中のポートを確認
lsof -i :8000
lsof -i :5432
lsof -i :6379

# docker-compose.ymlでポート変更
```

### Celery接続エラー

```bash
# Redisが起動しているか確認
docker-compose ps redis

# 手動でテスト
redis-cli -h localhost -p 6379 ping
```

### データベースエラー

```bash
# コンテナ再起動
docker-compose restart postgres

# ログ確認
docker-compose logs postgres

# データリセット
docker-compose down -v
docker-compose up -d
```

## 📚 次のステップ

1. [README.md](README.md) - 完全なドキュメント
2. [API Docs](http://localhost:8000/api/v1/docs) - インタラクティブAPI
3. [../BACKEND_ARCHITECTURE.md](../Veri-Train-UI/BACKEND_ARCHITECTURE.md) - 詳細設計

---

**Status**: ✅ 基本機能実装完了、開発可能
