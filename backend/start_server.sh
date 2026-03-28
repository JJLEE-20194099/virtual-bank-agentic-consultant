gunicorn main:app -k uvicorn.workers.UvicornWorker -w 18 -b 0.0.0.0:8080
# uvicorn main:app --reload --host 0.0.0.0 --port 8080