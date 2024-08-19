FROM ubuntu:latest

ARG TARGETARCH

ENV NODE_VERSION 20
ENV TINI_VERSION v0.19.0

RUN echo ">> Building for TARGETARCH=${TARGETARCH}, NODE_VERSION=${NODE_VERSION}, TINI_VERSION=${TINI_VERSION}"

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN <<EOF
    apt-get update --fix-missing 
    apt-get install -y make wget bzip2 ca-certificates curl git 
    apt-get clean 
    rm -rf /var/lib/apt/lists/*
EOF

COPY requirements.yml requirements.yml

RUN /bin/bash <<EOF
    if [ "${TARGETARCH}" == "arm64" ]; then 
        CONDA_ARCH="aarch64"
    else
        CONDA_ARCH=${TARGETARCH:-"x86_64"}
    fi
    # CONDA_ARCH expansion needs to be escaped to avoid docker expanding the variable before calling the shell
    echo "wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py310_24.5.0-0-Linux-\${CONDA_ARCH}.sh -O ~/miniconda.sh"
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py310_24.5.0-0-Linux-\${CONDA_ARCH}.sh -O ~/miniconda.sh 
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
    apt-get update && apt-get install yarn && apt-get install -y build-essential

# add tini
RUN /bin/bash <<EOF 
    if [ "${TARGETARCH}" == "x86_64" ]; then 
        TINI_FILE=tini
    else
        TINI_FILE=tini-${TARGETARCH} 
    fi
    # TINI_FILE expansion needs to be escaped to avoid docker expanding the variable before calling the shell
    echo "wget --quiet https://github.com/krallin/tini/releases/download/${TINI_VERSION}/\${TINI_FILE} -O /usr/bin/tini"
    wget --quiet https://github.com/krallin/tini/releases/download/${TINI_VERSION}/\${TINI_FILE} -O /usr/bin/tini   
    chmod +x /usr/bin/tini
EOF

RUN mkdir -p /dev/elyra

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/bin/bash" ]

