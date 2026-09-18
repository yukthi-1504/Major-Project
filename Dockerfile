FROM python:3.12-slim

WORKDIR /app

# Ecolab's network TLS-inspects outbound HTTPS via Zscaler; the base image
# doesn't trust that CA, so pip can't reach PyPI without it.
COPY zscaler-root-ca.crt /usr/local/share/ca-certificates/zscaler-root-ca.crt
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ml/ ml/
COPY api/ api/

EXPOSE 5000

WORKDIR /app/api
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
