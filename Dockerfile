FROM python:latest
WORKDIR /analyst
COPY . .
RUN pip install poetry
RUN poetry install
    
