FROM python:3.11-slim

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt update && apt install -y netcat-openbsd

COPY ./app .
COPY ./migration.sh .

# Run the migration script
ENTRYPOINT [ "./migration.sh" ]

# Run the application
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
EXPOSE 8000
