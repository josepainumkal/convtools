FROM virtualwatershed/vw-py
MAINTAINER Jose Painumkal

LABEL description="This Image builds an ubuntu 14.04 image from vw-py:1.0 and installs the dependencies of vw-webapp." \
      version="1.0"

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential \
    git wget curl unzip m4 openssh-client
RUN apt-get install -y libncurses5-dev
RUN apt-get update -y && apt-get install -y libpq-dev libssl-dev libffi-dev
# install nodejs
RUN curl -sL https://deb.nodesource.com/setup_4.x | sh -
RUN apt-get install -y nodejs
RUN npm install -g bower


# copy source code
COPY . /var/www/vwtools
WORKDIR /var/www/vwtools
ENV PYTHONPATH /var/www/vwtools

# install requirements
#RUN echo bakkas
RUN pip install -r requirements.txt


RUN echo '{ "allow_root": true }' > /root/.bowerrc
RUN bower install

# expose the app port
#EXPOSE 5001
ENV VWTOOLS_PORT 80
ENV VWTOOLS_HOST 0.0.0.0
EXPOSE ${VWTOOLS_PORT}
# run the app server
#ENTRYPOINT ["python"]
#CMD ["manage.py","runserver","-p","${VWADAPTOR_PORT}","-h","${VWADAPTOR_HOST}"]
CMD python manage.py runserver -p ${VWTOOLS_PORT} -h ${VWTOOLS_HOST}
