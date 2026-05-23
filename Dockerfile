FROM ubuntu:latest
LABEL authors="equip"

ENTRYPOINT ["top", "-b"]