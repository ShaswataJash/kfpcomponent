FROM python:3.7
RUN python3 -m pip install pycaret==2.3.10
RUN python3 -m pip install Jinja2==3.1.2
RUN apt update
RUN apt-get -y install ca-certificates fuse tzdata && echo "user_allow_other" >> /etc/fuse.conf
RUN curl https://rclone.org/install.sh | bash

COPY data_preparation.py /tmp
COPY run_tests.sh /tmp
RUN chmod 544 /tmp/run_tests.sh