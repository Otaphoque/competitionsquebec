# Set base image (host OS)
FROM python:3.12-alpine

# By default, listen on port 2004
EXPOSE 2004/tcp

# Set the working directory in the container
WORKDIR /competitionsquebec

# Copy the entire project to the working directory
COPY . .

# Install any dependencies
RUN pip install -r ./requirements.txt

# Specify the command to run on container start
CMD [ "python3", "./app.py" ]
