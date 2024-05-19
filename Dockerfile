FROM python:3.10.2

ENV DATABASE_URL="postgresql://postgres:123qwe123qwe@35.225.219.25/postgres"
ENV IAM_SERVICE_URL="https://iam.forge-code.com"

WORKDIR /code

# Create a virtual environment
RUN python -m venv venv
ENV PATH="/code/venv/bin:$PATH"

# Copy requirements file and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code
COPY ./app /code/app

# Expose port 8001
EXPOSE 8001

# Set the default command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
