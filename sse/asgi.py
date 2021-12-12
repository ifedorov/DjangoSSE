import django
from asgiref.sync import sync_to_async
from django.core.handlers.asgi import ASGIHandler


class ASGISseHandler(ASGIHandler):

    async def send_response(self, response, send):
        """Encode and send a response out over ASGI."""
        # Collect cookies into headers. Have to preserve header case as there
        # are some non-RFC compliant clients that require e.g. Content-Type.
        response_headers = []
        for header, value in response.items():
            if isinstance(header, str):
                header = header.encode('ascii')
            if isinstance(value, str):
                value = value.encode('latin1')
            response_headers.append((bytes(header), bytes(value)))
        for c in response.cookies.values():
            response_headers.append(
                (b'Set-Cookie', c.output(header='').encode('ascii').strip())
            )
        # Initial response message.
        await send({
            'type': 'http.response.start',
            'status': response.status_code,
            'headers': response_headers,
        })
        # Server side event responses need to be pinned to their iterator.
        if hasattr(response, 'sse_event') and response.sse_event:
            async for part in response:
                await send({
                    'type': 'http.response.body',
                    'body': part,
                    # Ignore "more" as there may be more parts; instead,
                    # use an empty final closing message with False.
                    'more_body': True,
                })

            # Final closing message.
            await send({'type': 'http.response.body'})
        # Streaming responses need to be pinned to their iterator.
        elif response.streaming and not hasattr(response, 'sse_event'):
            # Access `__iter__` and not `streaming_content` directly in case
            # it has been overridden in a subclass.
            for part in response:
                for chunk, _ in self.chunk_bytes(part):
                    await send({
                        'type': 'http.response.body',
                        'body': chunk,
                        # Ignore "more" as there may be more parts; instead,
                        # use an empty final closing message with False.
                        'more_body': True,
                    })
            # Final closing message.
            await send({'type': 'http.response.body'})
        # Other responses just need chunking.
        else:
            # Yield chunks of response.
            for chunk, last in self.chunk_bytes(response.content):
                await send({
                    'type': 'http.response.body',
                    'body': chunk,
                    'more_body': not last,
                })
        await sync_to_async(response.close, thread_sensitive=True)()


def get_asgi_application():
    django.setup(set_prefix=False)
    return ASGISseHandler()
