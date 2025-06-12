# 1) Use Python 3.11 base image
FROM python:3.11-slim

# 2) Create and set the working directory
WORKDIR /app

# Upgrade pip before installing dependencies
RUN pip install --upgrade pip

# 3) Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy the rest of the project code into /app
COPY . /app/

# 5) Expose the port on which your Django app will run
EXPOSE 8000


# 6) Command to start Django
# For production-like usage with Gunicorn, you can do:
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# (Replace "your_project_name" with your actual Django project folder)

# For local development, you might just do:
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8`000"]
