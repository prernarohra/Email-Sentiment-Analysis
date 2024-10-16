FROM python:3.9-slim 
#Defines the base image (e.g., python:3.9-slim).

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

#WORKDIR: Sets the working directory inside the container.
WORKDIR /app

#COPY: Copies files from your local machine into the container.
COPY requirements.txt .

#RUN: Executes a command (e.g., installing dependencies).
RUN pip install -r requirements.txt

#Copy the source code to the image
COPY . .

#CMD: Specifies the command to run when the container starts.
CMD ["uvicorn", "Email-check:app", "--reload", "--port", "8000"]





