FROM python:3.12-slim 

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY /app ./app

RUN mkdir -p /data && chown 10001:10001 /data /code

USER 10001
EXPOSE 5000 

CMD ["gunicorn","--bind" ,"0.0.0.0:5000","app:create_app()"]
