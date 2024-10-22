FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 4000

CMD ["flask","run","port=4000", "gunicorn", "-b", "0.0.0.0:5000", "app:app"]
