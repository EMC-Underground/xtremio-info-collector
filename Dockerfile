FROM python:alpine3.6

MAINTAINER Craig J Smith <craig.j.smith@dell.com>

WORKDIR /usr/src/app

COPY requirements.txt ./

COPY ca.crt /usr/local/share/ca-certificates/ca.crt

RUN pip install --no-cache-dir -r requirements.txt && \
    update-ca-certificates

COPY collector.py ./

CMD ["python", "./collector.py"]

