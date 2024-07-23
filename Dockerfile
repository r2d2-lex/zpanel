FROM python:3.9-alpine

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN apk add --no-cache libpq-dev
RUN pip install gunicorn
RUN pip install -r requirements.txt

COPY ./ .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app", "-k", "uvicorn.workers.UvicornWorker"]
