# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /app/

# Copy the application code before installing dependencies
COPY . /app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app/src

# Install the dependencies using Poetry without creating a virtual environment
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Expose the port where the FastAPI app will run
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["poetry", "run", "uvicorn", "src.pubmetric.api_controller:app", "--host", "0.0.0.0", "--port", "8000"]
