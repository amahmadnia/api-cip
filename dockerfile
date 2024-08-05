# Use Python 3.12.4 base image
FROM python:3.12.4

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy project files into the container
COPY . /code/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
