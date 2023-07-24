# Pull base image
FROM python:3.9-alpine

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory

WORKDIR /app

# Install dependencies
COPY ./requirements.txt .
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .build-deps \
    g++ gcc libxslt-dev
RUN apk add --update --no-cache --virtual .build-deps \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    lapack-dev \
    gfortran \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    libxml2-dev \
    libxslt-dev \
    postgresql-dev
RUN pip install -r requirements.txt
RUN pip install whitenoise
RUN pip install folium==0.14.0
RUN pip install django-crispy-forms
# Copy project
COPY . .