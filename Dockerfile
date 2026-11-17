FROM eclipse-temurin:21-jre-jammy

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-psycopg2 curl unzip \
    && rm -rf /var/lib/apt/lists/*

# Version and checksum from the Apache release; keep both in sync when upgrading.
RUN curl --fail --location --retry 3 \
        https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-6.2.0.zip \
        --output /tmp/fuseki.zip \
    && echo '46e5d798faf80fe5f4b32318750071b9172315f9d86bb3aa3ba4d5e94abe2e21cd194eab349d491a203c934c6e59b370a671b338f2a413110e859dc628ffe934  /tmp/fuseki.zip' | sha512sum --check \
    && unzip -q /tmp/fuseki.zip -d /opt \
    && mv /opt/apache-jena-fuseki-6.2.0 /opt/fuseki \
    && rm /tmp/fuseki.zip

# Compose publishes Fuseki only on the host's loopback interface.
RUN printf '[urls]\n/** = anon\n' > /opt/fuseki/shiro-local.ini

ENV PYTHONUNBUFFERED=1 FUSEKI_HOME=/opt/fuseki FUSEKI_BASE=/tmp/fuseki
WORKDIR /app
COPY r2rml.jar ./
COPY dependency/ ./dependency/
COPY submit/Database/ ./submit/Database/
COPY submit/mapping.ttl submit/SPARQL.ipynb ./submit/
COPY submit/Deployment/show/ ./submit/Deployment/show/
COPY scripts/ ./scripts/
