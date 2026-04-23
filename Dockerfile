FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY --chown=user . /app

EXPOSE 7860

CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.port=7860", "--server.address=0.0.0.0"]