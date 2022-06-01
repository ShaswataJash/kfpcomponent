
FROM python:3.7
RUN python3 -m pip install pycaret==2.3.10
RUN python3 -m pip install Jinja2==3.1.2
RUN curl https://rclone.org/install.sh | bash

COPY data_preparation.py /tmp
COPY run_tests.sh /tmp