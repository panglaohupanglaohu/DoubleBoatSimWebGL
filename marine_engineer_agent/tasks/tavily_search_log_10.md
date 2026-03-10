Traceback (most recent call last):
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/connection.py", line 204, in _new_conn
    sock = connection.create_connection(
        (self._dns_host, self.port),
    ...<2 lines>...
        socket_options=self.socket_options,
    )
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/util/connection.py", line 85, in create_connection
    raise err
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/util/connection.py", line 73, in create_connection
    sock.connect(sa)
    ~~~~~~~~~~~~^^^^
ConnectionRefusedError: [Errno 61] Connection refused

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/connectionpool.py", line 773, in urlopen
    self._prepare_proxy(conn)
    ~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/connectionpool.py", line 1042, in _prepare_proxy
    conn.connect()
    ~~~~~~~~~~~~^^
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/connection.py", line 759, in connect
    self.sock = sock = self._new_conn()
                       ~~~~~~~~~~~~~~^^
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/connection.py", line 219, in _new_conn
    raise NewConnectionError(
        self, f"Failed to establish a new connection: {e}"
    ) from e
urllib3.exceptions.NewConnectionError: HTTPSConnection(host='127.0.0.1', port=7897): Failed to establish a new connection: [Errno 61] Connection refused

The above exception was the direct cause of the following exception:

urllib3.exceptions.ProxyError: ('Unable to connect to proxy', NewConnectionError("HTTPSConnection(host='127.0.0.1', port=7897): Failed to establish a new connection: [Errno 61] Connection refused"))

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/homebrew/lib/python3.14/site-packages/requests/adapters.py", line 644, in send
    resp = conn.urlopen(
        method=request.method,
    ...<9 lines>...
        chunked=chunked,
    )
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(
        method, url, error=new_e, _pool=self, _stacktrace=sys.exc_info()[2]
    )
  File "/opt/homebrew/lib/python3.14/site-packages/urllib3/util/retry.py", line 535, in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='api.tavily.com', port=443): Max retries exceeded with url: /search (Caused by ProxyError('Unable to connect to proxy', NewConnectionError("HTTPSConnection(host='127.0.0.1', port=7897): Failed to establish a new connection: [Errno 61] Connection refused")))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<string>", line 9, in <module>
    result1 = client.search(
        query='ship energy management system optimization predictive maintenance',
        search_depth='advanced',
        include_answer=True
    )
  File "/opt/homebrew/lib/python3.14/site-packages/tavily/tavily.py", line 170, in search
    response_dict = self._search(query,
                                 search_depth=search_depth,
    ...<16 lines>...
                                 exact_match=exact_match,
                                 **kwargs)
  File "/opt/homebrew/lib/python3.14/site-packages/tavily/tavily.py", line 119, in _search
    response = self.session.post(url, data=payload, timeout=timeout)
  File "/opt/homebrew/lib/python3.14/site-packages/requests/sessions.py", line 637, in post
    return self.request("POST", url, data=data, json=json, **kwargs)
           ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/lib/python3.14/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/homebrew/lib/python3.14/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/homebrew/lib/python3.14/site-packages/requests/adapters.py", line 671, in send
    raise ProxyError(e, request=request)
requests.exceptions.ProxyError: HTTPSConnectionPool(host='api.tavily.com', port=443): Max retries exceeded with url: /search (Caused by ProxyError('Unable to connect to proxy', NewConnectionError("HTTPSConnection(host='127.0.0.1', port=7897): Failed to establish a new connection: [Errno 61] Connection refused")))
Searching: ship energy management system optimization...
