#!/bin/bash

# # Update packages
# sudo dnf update -d 0 -e 0 -y
#
# Install packages
sudo dnf install -d 0 -e 0 -y \
    createrepo \
    libsass \
    postgresql \
    postgresql-contrib \
    postgresql-devel \
    postgresql-libs \
    postgresql-server \
    python3-PyPDF2 \
    python3-cryptography \
    python3-babel \
    python3-chardet \
    python3-dateutil \
    python3-decorator \
    python3-devel \
    python3-docutils \
    python3-freezegun \
    python3-gevent \
    python3-greenlet \
    python3-idna \
    python3-jinja2 \
    python3-libsass \
    python3-lxml \
    python3-markupsafe \
    python3-mock \
    python3-num2words \
    python3-ofxparse \
    python3-passlib \
    python3-pillow \
    python3-polib \
    python3-psutil \
    python3-psycopg2 \
    python3-pydot \
    python3-pyldap \
    python3-pyOpenSSL \
    python3-pyserial \
    python3-pytz \
    python3-pyusb \
    python3-qrcode \
    python3-reportlab \
    python3-requests \
    python3-six \
    python3-stdnum \
    python3-vobject \
    python3-werkzeug \
    python3-wheel \
    python3-xlrd \
    python3-xlsxwriter \
    python3-xlwt \
    python3-zeep \
    rpmdevtools

# Clean up
sudo dnf clean all
