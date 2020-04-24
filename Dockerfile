FROM python:2.7-buster

RUN apt-get update && apt-get install -y \
      sudo \
      apt-utils \
      wget \
      git \
      make \
      libcurl4 \
      libgif7 \
      libpixman-1-0 \
      ghostscript \
      gsfonts \
      gunicorn3 \
      w3c-sgml-lib \
      subversion \
      libfontconfig1 \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/* 

# Install fonts
# NOTE: must enable contrib apt repository for msttcorefonts
# NOTE: must remove bitmap-fonts.conf due to fontconfig bug
RUN sed -i 's/$/ contrib/' /etc/apt/sources.list \
  && apt-get update && apt-get install --assume-yes \
     fontconfig \
     msttcorefonts \
     fonts-arphic-bkai00mp fonts-arphic-bsmi00lp fonts-arphic-gbsn00lp \
     fonts-ipafont-gothic fonts-ipafont-mincho fonts-lato fonts-lmodern fonts-sil-padauk fonts-unfonts-core fonts-unfonts-extra  \
     ttf-unifont \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && rm /etc/fonts/conf.d/10-scale-bitmap-fonts.conf

# Install PrinceXML
ENV PRINCE=prince_13.1-1_debian10_amd64.deb
RUN wget https://www.princexml.com/download/$PRINCE \
  && dpkg -i $PRINCE \
  && rm -r $PRINCE

# install python requirements
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt 

ADD src /usr/lib/kolekti

RUN update-alternatives --install /usr/bin/kolekti  kolekti /usr/lib/kolekti/kolekti_run.py 1

ENV LANG C.UTF-8

