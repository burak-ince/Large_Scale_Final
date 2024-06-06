FROM python:3.11.4

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3","run.py"]