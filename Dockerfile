FROM cr.yandex/yc/samples/python3.12:latest
COPY lambda_function.py /function/
RUN pip install --no-cache-dir boto3 requests
