FROM python:3-alpine
WORKDIR /hello
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . ./
ENTRYPOINT ["python3", "hello.py"]
