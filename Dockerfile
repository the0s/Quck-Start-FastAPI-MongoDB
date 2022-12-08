FROM python:3.7

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

EXPOSE 5555
