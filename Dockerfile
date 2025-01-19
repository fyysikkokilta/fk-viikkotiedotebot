FROM python:3.12-slim

COPY . /bot
WORKDIR /bot
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["bot.py"]