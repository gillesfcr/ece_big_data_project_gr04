# Spark + Jupyter image used by every step of the project (batch jobs,
# enrichment scraper, Kafka producer and streaming job).
# Pinned by digest: quay.io/jupyter/pyspark-notebook with Spark 4.2.0,
# Scala 2.13 and Python 3.13.
FROM quay.io/jupyter/pyspark-notebook@sha256:80430186e2e97c5e0a9a3c117798d4007bc0a289b8a72cf3a9fc92f044b4c4f1

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# The data directory is a named volume: creating it here with the right owner
# lets Docker initialise the volume with jovyan as owner.
RUN mkdir -p /home/jovyan/project/data \
    && fix-permissions /home/jovyan/project

WORKDIR /home/jovyan/project
