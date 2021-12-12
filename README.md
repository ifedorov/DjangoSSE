# POC - Django Server Side Events
## Important 
Django entrypoint asgi replaced with custom 
Pay attention on 
```python
from sse.asgi import get_asgi_application
```
in config/asgi.py


### Install 

```python
pip install "Django>=3.1.0"
pip install uvicorn gunicorn
```

### Run 

```python
python manage.py migrate
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker
```

http://127.0.0.1:8000 