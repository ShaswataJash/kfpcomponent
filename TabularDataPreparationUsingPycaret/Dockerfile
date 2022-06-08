FROM python:3.7.13-slim

RUN python3 -m pip install pycaret==2.3.10
#installing jinja2 additionally due to Ref: https://github.com/pycaret/pycaret/issues/2490
RUN python3 -m pip install Jinja2==3.1.2

#install fuse as dependency for rclone. Additionally, install curl, unzip for rclone installer to work
#libgomp1 installation for pycaret in python-slim
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl fuse libgomp1 unzip \
    && echo "user_allow_other" >> /etc/fuse.conf \
    && curl https://rclone.org/install.sh \
    && apt-get -y remove --purge curl unzip \
    && rm -rf /var/lib/apt/lists/* \
    && rclone --version

COPY src/data_preparation.py /tmp
COPY tests/test_validation.py /tmp
COPY run_tests.sh /tmp
RUN chmod 544 /tmp/run_tests.sh