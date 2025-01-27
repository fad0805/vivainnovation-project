FROM python:3.11-slim

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./api .
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
EXPOSE 8000
