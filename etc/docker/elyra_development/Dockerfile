FROM ubuntu:latest

ARG TARGETARCH

ENV NODE_VERSION 16
ENV TINI_VERSION v0.19.0

RUN echo ">> Building for TARGETARCH=${TARGETARCH}, NODE_VERSION=${NODE_VERSION}, TINI_VERSION=${TINI_VERSION}"

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y make wget bzip2 ca-certificates curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.yml requirements.yml

RUN <<EOF
    export CONDA_ARCH=$(uname -m) 
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py310_24.5.0-0-Linux-${CONDA_ARCH}.sh -O ~/miniconda.sh 
    /bin/bash ~/miniconda.sh -b -p /opt/conda 
    rm ~/miniconda.sh 
    /opt/conda/bin/conda clean -tipy 
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh 
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc 
    echo "conda activate elyra-env" >> ~/.bashrc 
    /opt/conda/bin/conda env create --file requirements.yml
EOF

# update nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get install -y nodejs

# install yarn
RUN curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && apt-get install yarn

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${TARGETARCH} /usr/bin/tini
RUN chmod +x /usr/bin/tini

RUN mkdir -p /dev/elyra

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/bin/bash" ]

