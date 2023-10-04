# Dockerfile, Image, Container
FROM python:3.11
WORKDIR /app
COPY ./requirement.txt /app/requirement.txt
RUN set -x \
    && apt update \
    && apt upgrade -y \
    && apt install -y firefox-esr \
    && pip install --no-cache-dir --upgrade -r /app/requirement.txt
COPY . /app
CMD ["uvicorn", "Api.main:app", "--port", "80", "--host", "0.0.0.0"]