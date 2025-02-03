FROM python:3.8

# Create folders
RUN mkdir /app
RUN mkdir /app/outputs
WORKDIR /app

# Copy the Python script into the container
COPY crawl_async.py /app
COPY sharing.py /app
ADD requirements.txt /app/

# Install Python dependencies
RUN pip install -r requirements.txt

# Run playwright install to ensure all browsers are downloaded
RUN playwright install --with-deps

# Command to run the web scraping script
CMD ["python", "crawl_async.py"]
