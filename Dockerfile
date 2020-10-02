ARG ARCH
FROM ${ARCH}/python:alpine3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 9112

CMD [ "python", "-u", "src/exporter.py" ]
