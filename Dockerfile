FROM python:3.9-slim
WORKDIR /app
RUN pip install requests netifaces
COPY . .
RUN python setup.py install
ENTRYPOINT ["aliyun-ddns"]