FROM python:3.10-alpine

WORKDIR /opt/autopayments/
COPY ./ ./

RUN python3 setup.py sdist bdist_wheel
RUN pip install dist/*.whl

RUN chmod +x docker-entrypoint.sh
CMD ["./docker-entrypoint.sh"]