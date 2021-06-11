FROM python:3.7-stretch
ENV TZ=Asia/Shanghai
EXPOSE 80
RUN apt-get update
RUN apt-get install --no-install-recommends -y net-tools lrzsz apt-transport-https vim  curl gnupg git redis-server supervisor software-properties-common wget
RUN curl https://openresty.org/package/pubkey.gpg | apt-key add -
RUN add-apt-repository -y "deb http://openresty.org/package/debian stretch openresty"
RUN apt-get update
RUN apt-get install -y openresty
COPY ./deploy /fiddler_tools/deploy
RUN pip install --upgrade pip setuptools==45.2.0
RUN pip install -i https://pypi.douban.com/simple/ -r /fiddler_tools/deploy/pyenv/requirements.txt -U
RUN cp /fiddler_tools/deploy/nginx/*.conf /usr/local/openresty/nginx/conf/
RUN cp /fiddler_tools/deploy/supervisor/*.conf /etc/supervisor/conf.d/
COPY ./client/dist /fiddler_tools/client/dist
COPY server /fiddler_tools/server
WORKDIR /fiddler_tools/server
COPY ./docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh
CMD ["./docker-entrypoint.sh"]
