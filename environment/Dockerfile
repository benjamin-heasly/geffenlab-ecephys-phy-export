# hash:sha256:8cb418750b941afdc42885fbfc5945b0ba9432deb9a8e985fd76fdd746097e3a
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    phylib==2.6.0 \
    scikit-learn==1.6.1 \
    spikeinterface[full]==0.102.1
