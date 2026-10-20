FROM python:3.11.0

WORKDIR /app

# COPY alembic.ini /app/
# COPY alembic /app/alembic
COPY requirements.txt /app/


# --no-cache-dir: otherwise pip keeps a second copy of every downloaded wheel in /root/.cache/pip
RUN pip install --no-cache-dir --upgrade pip
# Install opencompass without dependencies to avoid pyext compatibility issues with Python 3.11
RUN pip install --no-cache-dir opencompass==0.5.1 --no-deps
# torch is only needed because the eval dataset sampler imports opencompass.utils; nothing here runs on a
# GPU, so install the CPU build first and requirements.txt's torch line is already satisfied. The default
# PyPI wheel pulls ~3 GB of CUDA libraries (nvidia-*, triton).
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r ./requirements.txt
# RUN pip install .

COPY . .