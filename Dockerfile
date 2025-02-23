# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy only necessary files to optimize build
COPY requirements.txt ./
COPY main.py ./
COPY whatsapp_utils.py ./
COPY serviceAccountKey.json ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables securely (Use actual values in your deployment)
ENV VERIFY_TOKEN=my_secure_token
ENV WHATSAPP_ACCESS_TOKEN=my_whatsapp_token

# Expose port 8080 for the webhook
EXPOSE 8080

# Run the application
CMD ["functions-framework", "--target=whatsapp_webhook", "--port=8080"]
