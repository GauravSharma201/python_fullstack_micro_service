```bash

python main.py
INFO:     Started server process [18904]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:60629 - "GET /ui/ HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_transports\default.py", line 66, in map_httpcore_exceptions
    yield
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_transports\default.py", line 366, in handle_async_request
    resp = await self._pool.handle_async_request(req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpcore\_async\connection_pool.py", line 256, in handle_async_request
    raise exc from None
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpcore\_async\connection_pool.py", line 236, in handle_async_request
    response = await connection.handle_async_request(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        pool_request.request
        ^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpcore\_async\connection.py", line 101, in handle_async_request
    raise exc
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpcore\_async\connection.py", line 78, in handle_async_request
    stream = await self._connect(request)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpcore\_async\connection.py", line 124, in _connect
    stream = await self._network_backend.connect_tcp(**kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpcore\_backends\auto.py", line 31, in connect_tcp
    return await self._backend.connect_tcp(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
    )
    ^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpcore\_backends\anyio.py", line 113, in connect_tcp
    with map_exceptions(exc_map):
         ~~~~~~~~~~~~~~^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.1520.0_x64__qbz5n2kfra8p0\Lib\contextlib.py", line 162, in __exit__
    self.gen.throw(value)
    ~~~~~~~~~~~~~~^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpcore\_exceptions.py", line 14, in map_exceptions
    raise to_exc(exc) from exc
httpcore.ConnectError: [Errno 11001] getaddrinfo failed

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 426, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 84, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\fastapi\applications.py", line 1106, in __call__
    await super().__call__(scope, receive, send)
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\applications.py", line 122, in __call__
    await self.middleware_stack(scope, receive, send)
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\middleware\errors.py", line 184, in __call__
    raise exc
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\middleware\errors.py", line 162, in __call__
    await self.app(scope, receive, _send)
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\middleware\cors.py", line 83, in __call__
    await self.app(scope, receive, send)
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\middleware\exceptions.py", line 79, in __call__
    raise exc
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\middleware\exceptions.py", line 68, in __call__
    await self.app(scope, receive, sender)
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 20, in __call__
    raise e
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 17, in __call__
    await self.app(scope, receive, send)
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\routing.py", line 718, in __call__
    await route.handle(scope, receive, send)
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\routing.py", line 276, in handle
    await self.app(scope, receive, send)
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\starlette\routing.py", line 66, in app
    response = await func(request)
               ^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\fastapi\routing.py", line 274, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        dependant=dependant, values=values, is_coroutine=is_coroutine
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\fastapi\routing.py", line 191, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\main.py", line 83, in ui_proxy
    response = await forward_request(
               ^^^^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
    )
    ^
  File "D:\python-learning\micro-service-python-backend\gateway\main.py", line 35, in forward_request
    response = await client.request(
               ^^^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
    )
    ^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_client.py", line 1530, in request
    return await self.send(request, auth=auth, follow_redirects=follow_redirects)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_client.py", line 1617, in send
    response = await self._send_handling_auth(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
    )
    ^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_client.py", line 1645, in _send_handling_auth
    response = await self._send_handling_redirects(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_client.py", line 1682, in _send_handling_redirects
    response = await self._send_single_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_client.py", line 1719, in _send_single_request
    response = await transport.handle_async_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_transports\default.py", line 365, in handle_async_request
    with map_httpcore_exceptions():
         ~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.1520.0_x64__qbz5n2kfra8p0\Lib\contextlib.py", line 162, in __exit__
    self.gen.throw(value)
    ~~~~~~~~~~~~~~^^^^^^^
  File "D:\python-learning\micro-service-python-backend\gateway\venv\Lib\site-packages\httpx\_transports\default.py", line 83, in map_httpcore_exceptions
    raise mapped_exc(message) from exc
httpx.ConnectError: [Errno 11001] getaddrinfo failed
```
