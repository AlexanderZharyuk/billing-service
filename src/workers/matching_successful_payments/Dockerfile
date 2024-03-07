FROM python:3.10-alpine

WORKDIR /opt

COPY ./ ./
COPY .env-example .env

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python3", "-m", "src.workers.matching_successful_payments.main"]