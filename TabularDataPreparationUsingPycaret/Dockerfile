FROM python:3.7.13-slim
RUN python3 -m pip install pycaret==2.3.10
RUN python3 -m pip install Jinja2==3.1.2
RUN apt update
RUN apt-get -y install ca-certificates tzdata fuse rclone && echo "user_allow_other" >> /etc/fuse.conf

COPY src/data_preparation.py /tmp
COPY tests/test_validation.py /tmp
COPY run_tests.sh /tmp
RUN chmod 544 /tmp/run_tests.sh