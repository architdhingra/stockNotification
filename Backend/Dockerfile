FROM python:3.7
COPY ./* ./Backend/
WORKDIR /Backend/
RUN python -m pip install -r requirements.txt
CMD [ "python", "StockPrice.py"]