FROM python:3

FROM gorialis/discord.py

RUN mkdir -p /usr/src/bot

WORKDIR /usr/src/bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "app.py" ]
