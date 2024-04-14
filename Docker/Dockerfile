ARG version=16
# Use an official PostgreSQL runtime as a parent image
FROM postgres:${version}

ARG version

# Set the environment variables for PostgreSQL from a .env file
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

# Environment Flags
ENV PARADEDB_TELEMETRY=false

# Install necessary tools for building from source
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    libssl-dev \
    pkg-config \
    wget

# Download and extract ICU source code
RUN wget https://github.com/unicode-org/icu/releases/download/release-70-1/icu4c-70_1-src.tgz \
    && tar -zxvf icu4c-70_1-src.tgz

# Build and install ICU
WORKDIR /icu/source
RUN ./configure --prefix=/usr \
    && make \
    && make install

# Clean up
WORKDIR /
RUN rm -rf /icu


# # Download and install libicu70
RUN apt-get install -y curl
RUN curl -L "https://github.com/paradedb/paradedb/releases/download/v0.6.0/pg_search-v0.6.0-pg${version}-arm64-ubuntu2204.deb" -o /tmp/pg_search.deb 
RUN apt install -y --no-install-recommends /tmp/*.deb

RUN apt install postgresql-16-pgvector
## IUnst

# Copy the custom configuration file into the Docker image
RUN echo "listen_addresses = '*'\nshared_preload_libraries = 'pg_search'" > /etc/postgresql/postgresql.conf


# Expose PostgreSQL port
EXPOSE 5432

COPY ./init.sql /docker-entrypoint-initdb.d/


# Set the command to start PostgreSQL with the custom configuration file
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]