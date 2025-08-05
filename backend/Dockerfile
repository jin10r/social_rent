FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make wait script executable
RUN chmod +x wait_for_db.py

# Expose port
EXPOSE 8001

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for database..."\n\
python wait_for_db.py\n\
if [ $? -eq 0 ]; then\n\
    echo "Database is ready, starting application..."\n\
    exec uvicorn main:app --host 0.0.0.0 --port 8001 --reload\n\
else\n\
    echo "Failed to connect to database"\n\
    exit 1\n\
fi' > /app/start.sh && chmod +x /app/start.sh

# Command to run the application
CMD ["/app/start.sh"]