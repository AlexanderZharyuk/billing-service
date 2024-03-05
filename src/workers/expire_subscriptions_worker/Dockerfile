FROM python:3.10-alpine

COPY ./ /opt/

WORKDIR /opt/src/workers/expire_subscriptions_worker/

RUN python3 setup.py sdist bdist_wheel
RUN pip install dist/*.whl

RUN chmod +x docker-entrypoint.sh
#CMD ["./docker-entrypoint.sh"]
CMD ["tail", "-f", "/dev/null"]