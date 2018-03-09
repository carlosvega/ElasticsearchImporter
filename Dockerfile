FROM ubuntu:16.04
MAINTAINER Carlos Vega <carlos.vega@naudit.es>
RUN apt-get update -y
RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true apt-get install -y apt-utils tzdata
RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true dpkg-reconfigure tzdata
RUN echo "Europe/Madrid" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get update -y
RUN apt-get install -y git build-essential
RUN git clone https://github.com/carlosvega/ElasticsearchImporter.git ElasticsearchImporter
WORKDIR ElasticsearchImporter
RUN bash ./install.bash