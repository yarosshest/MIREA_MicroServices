FROM python:3.10
WORKDIR /EmployeeApi
ENV PYTHONPATH="${PYTHONPATH}:/EmployeeApi"

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

COPY . .

CMD [ "uvicorn", "main:api", "--host", "0.0.0.0" , "--port", "8031"]