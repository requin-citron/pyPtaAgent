FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
COPY utils/ utils/
COPY amqp/ amqp/
COPY xml_parser/ xml_parser/
COPY pyPTaAgent.py .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "pyPTaAgent.py"]
CMD ["--help"]