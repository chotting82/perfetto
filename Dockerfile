FROM python:3

RUN git clone https://github.com/chotting82/perfetto /opt/perfetto

WORKDIR /opt/perfetto

RUN tools/install-build-deps --ui

ENTRYPOINT ["./ui/run-dev-server", "--serve-host", "0.0.0.0"]