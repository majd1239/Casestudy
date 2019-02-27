FROM python:3.6

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

COPY ./configs ./configs

COPY app.py .

COPY run_app.sh .

RUN chmod 755 run_app.sh

CMD ["./run_app.sh"]
