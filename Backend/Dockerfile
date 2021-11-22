FROM python:3.7
COPY ./* ./Backend/
WORKDIR /Backend/
RUN python -m pip install -r requirements.txt
EXPOSE 8080
ENV FLASK_APP=controller.py
ENV FLASK_ENV=development
CMD [ "python3", "-m" , "flask", "run", "--port=8080"]