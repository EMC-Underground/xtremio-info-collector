FROM python:alpine3.6

MAINTAINER Craig J Smith <craig.j.smith@dell.com>

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && \

COPY collector.py ./

CMD ["python", "./collector.py"]

