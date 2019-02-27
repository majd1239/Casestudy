FROM python:3.6

RUN pip3 install sanic

COPY ./mock_data ./mock_data

COPY ./app.py .

CMD ["python3","app.py"]
