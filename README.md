# xtremio-info-collector

To build with Root CA:

docker build -t <image-name> .

To build without cert:

docker build -t <image-name> Dockerfile-cert

This container accepts the following environment variables:

XMS_IP (required)
XIO_NAME (default: null)
USER (required)
PASSWORD (required)
TARGET_API_URL (required)
LOG_LEVEL (default: INFO)
VERIFY_CERT (default: ca-certificates)


example run command:

docker run -e "XMS_IP=10.10.10.10" -e "USERNAME=admin" -e "PASSWORD=p@ssw0rd" -e "TARGET_API_URL=http://api.endpoint.com/storage/v1/array" -e "VERIFY_CERT=False" -e "LOG_LEVEL=DEBUG" xtremio-collector:latest
