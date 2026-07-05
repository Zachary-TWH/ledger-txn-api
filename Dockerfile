# use official Python image as base
FROM python:3.11-slim

# set working directory inside the container
WORKDIR /app

# copy requirements first (so Docker caches this layer)
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the rest of the project
COPY . .

# start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]