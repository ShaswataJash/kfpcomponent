FROM python:3.7.13-slim

#install fuse as dependency for rclone. Additionally, install curl, unzip for rclone installer to work
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl fuse unzip \
    && echo "user_allow_other" >> /etc/fuse.conf \
    && curl https://rclone.org/install.sh | bash \
    && apt-get -y remove --purge curl unzip \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/* \
    && rclone --version

#install kaggle client lib
RUN python3 -m pip install kaggle==1.5.12
    
COPY src/kaggle_download.py /tmp
COPY tests/test_validation.py /tmp
COPY run_tests.sh /tmp
RUN chmod 544 /tmp/run_tests.sh
