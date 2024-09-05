# Use the official Python 3.10 image as the base image
FROM python:3.11

# create dorectory for the application
RUN mkdir /opt/app

# create a user for the application
RUN useradd -r -s /bin/nologin  botrunner


# set the working directory
WORKDIR /opt/app

# make the botrunner the owner of the application directory
RUN chown botrunner:botrunner /opt/app

# copy all files from the current directory to the container
COPY . .

# install the dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Get the password from the command line builmd arguments
ARG password=""

# Add the password to the environement variables
ENV PASSWORD=$password

# Run the application as the botrunner user
USER botrunner
CMD ["python3", "main.py", "$PASSWORD"]
