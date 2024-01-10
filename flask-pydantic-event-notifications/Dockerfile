# Copy the current directory contents into the container at /usr/src/app
COPY ./app .

# Install any needed packages specified in requirements.txt
RUN pip install Flask pydantic minio psycopg2 

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run app.py when the container launches
CMD ["flask", "run"]
