FROM python:3.6

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./src ./src

COPY ./configs ./configs

COPY ./main.py .

RUN chmod -R 777 /opt

CMD ["python3", "./main.py"]
