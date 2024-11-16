FROM python:3.10
WORKDIR /TaskApi
ENV PYTHONPATH="${PYTHONPATH}:/TaskApi"

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

COPY . .

CMD [ "uvicorn", "main:api", "--host", "0.0.0.0" , "--port", "8032", "--log-level", "debug"]