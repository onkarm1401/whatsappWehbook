# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache for dependencies
COPY requirements.txt ./

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all Python files to the working directory
COPY . ./

# Set environment variables securely (Use actual values in your deployment)
ENV VERIFY_TOKEN=my_secure_token
ENV WHATSAPP_ACCESS_TOKEN=my_whatsapp_token

# Expose port 8080 for the webhook
EXPOSE 8080

# Run the application
CMD ["functions-framework", "--target=whatsapp_webhook", "--port=8080"]
