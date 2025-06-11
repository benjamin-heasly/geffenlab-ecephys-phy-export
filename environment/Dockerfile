# hash:sha256:f4f6610f87ff3b50110dbac7a0163bfc4e65955961805e86a7833c451892f813
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/mambaforge3:24.5.0-0-python3.12.4-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    numpy==2.2.6 \
    phylib==2.6.0 \
    scikit-learn==1.6.1 \
    spikeinterface[full]==0.102.1
