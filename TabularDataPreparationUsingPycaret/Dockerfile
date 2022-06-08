FROM python:3.7.13-slim

RUN python3 -m pip install pycaret==2.3.10
#installing jinja2 additionally due to Ref: https://github.com/pycaret/pycaret/issues/2490
RUN python3 -m pip install Jinja2==3.1.2

RUN apt update
RUN apt-get -y install ca-certificates tzdata fuse curl && echo "user_allow_other" >> /etc/fuse.conf
RUN curl https://rclone.org/install.sh | bash
RUN rclone --version

#libgomp1 installation for pycaret in python-slim
RUN apt-get -y install libgomp1

COPY src/data_preparation.py /tmp
COPY tests/test_validation.py /tmp
COPY run_tests.sh /tmp
RUN chmod 544 /tmp/run_tests.sh