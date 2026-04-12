# Pythonベース
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係コピー
COPY requirements.txt .

# インストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリコピー
COPY . .

# ポート公開
EXPOSE 8000

# 起動コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]