# -*- mode: dockerfile -*-
# Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "LICENSE.txt" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for
# the specific language governing permissions and limitations under the License.
ARG djl_version=0.18.0~SNAPSHOT
FROM arm64v8/ubuntu:20.04

EXPOSE 8080

COPY dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh
RUN chmod +x /usr/local/bin/dockerd-entrypoint.sh
WORKDIR /opt/djl
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
ENV OMP_NUM_THREADS=1
ENV JAVA_OPTS="-Dai.djl.pytorch.num_interop_threads=1"
ENV MODEL_SERVER_HOME=/opt/djl

ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
CMD ["serve"]

COPY scripts scripts/
RUN mkdir -p /opt/djl/conf
COPY config.properties /opt/djl/conf/

COPY https://publish.djl.ai/djl-serving/djl-serving_${djl_version}-1_all.deb ./djl-serving_all.deb
RUN scripts/install_djl_serving.sh
RUN scripts/install_python.sh
RUN rm -rf scripts djl-serving_all.deb
RUN apt-get clean -y && rm -rf /var/lib/apt/lists/*
RUN djl-serving -i ai.djl.pytorch:pytorch-native-cpu-precxx11:1.11.0:linux-aarch64

LABEL maintainer="djl-dev@amazon.com"