FROM python:3.7.13-slim

RUN python3 -m pip install pandas-profiling==3.2.0
#pandas-profiling 3.2 will download markupsafe-2.1.1 which is not compatible with itself. So it has to be replaced with older markupsafe
RUN python3 -m pip install markupsafe==2.0.1
#beautifulsoup4 and lxml are needed for test validation
RUN python3 -m pip install beautifulsoup4==4.11.1
RUN python3 -m pip install lxml==4.9.0

#install fuse as dependency for rclone. Additionally, install curl, unzip for rclone installer to work
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl fuse unzip \
    && echo "user_allow_other" >> /etc/fuse.conf \
    && curl https://rclone.org/install.sh | bash \
    && apt-get -y remove --purge curl unzip \
    && rm -rf /var/lib/apt/lists/* \
    && rclone --version

COPY src/data_visualization.py /tmp
COPY tests/test_validation.py /tmp
COPY run_tests.sh /tmp
RUN chmod 544 /tmp/run_tests.sh