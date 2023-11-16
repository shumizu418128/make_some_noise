# ベースイメージとしてPython 3.11を使用
FROM python:3.11

# 環境変数を一度に設定
ENV LANG=ja_JP.UTF-8 \
    LANGUAGE=ja_JP:ja \
    LC_ALL=ja_JP.UTF-8 \
    TZ=JST-9 \
    TERM=xterm

# Pythonのpipをアップグレード
RUN /usr/local/bin/python -m pip install --upgrade pip

# pipでPythonパッケージをインストール
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

# apt-getコマンドで必要なパッケージをインストールし、クリーンアップ
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ファイルをコピー
COPY main.py /app/
COPY mp3/*.mp3 /app/
COPY *.gif /app/
COPY *.py /app/
COPY *.json /app/
COPY *.png /app/
COPY *.traineddata /app/

# 作業ディレクトリを/appに設定
WORKDIR /app

# コマンドを指定
CMD ["python", "-u", "main.py"]
