FROM python:3.11.0

WORKDIR /app

# COPY alembic.ini /app/
# COPY alembic /app/alembic
COPY requirements.txt /app/


RUN pip install --upgrade pip
# Install opencompass without dependencies to avoid pyext compatibility issues with Python 3.11
RUN pip install opencompass==0.5.1 --no-deps
RUN pip install -r ./requirements.txt
# RUN pip install .

COPY . .