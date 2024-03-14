FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rembg d
COPY . .

CMD [ "python", "./discord_bot.py" ]