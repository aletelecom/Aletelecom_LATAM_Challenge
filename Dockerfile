#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
FROM python:3.9

# 
WORKDIR /app

# 
COPY ./requirements.txt /app/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
#RUN rm main.py

# 
COPY ./challenge /app/challenge
COPY ./ml_models /app/ml_models
COPY ./data /app/data

# 
CMD ["uvicorn", "challenge.api:app", "--reload", "--host", "127.0.0.1", "--port", "80"]
