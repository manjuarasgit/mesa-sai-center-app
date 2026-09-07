FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY mesa_sai_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "mesa_sai_app.app:app", "--host", "0.0.0.0", "--port", "8000"]
