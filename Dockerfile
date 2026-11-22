FROM python:3.13-alpine

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN apk add --no-cache libpq-dev
RUN pip install gunicorn
RUN pip install -r requirements.txt
RUN pip install sqlalchemy[asyncio]

COPY ./ .

RUN mkdir -p ./static/images

ENV PYTHONPATH=/app/app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.main:app", "-k", "uvicorn.workers.UvicornWorker"]
