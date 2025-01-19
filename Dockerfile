#FROM python:3.10
#
#WORKDIR /app
#COPY . .
#COPY requirements.txt /app/requirements.txt
#RUN  pip install --no-cache-dir -r /app/requirements.txt
#CMD ["python", "main.py"]
##docker exec -it pg psql -U postgres
FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y docker.io

COPY . .

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "main.py"]
