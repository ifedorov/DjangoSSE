import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponseBase


class ServerSideEventHttpResponse(HttpResponseBase):
    sse_event = True
    streaming = True

    def sse_event(self, event_type, data):
        return 'event: {}\nid: {}\ndata: {}\n\n'.format(
            event_type,
            self.event_id,
            json.dumps(data, cls=DjangoJSONEncoder)
        )

    def __init__(self, streaming_content=(), event_type='test', content_type=None, *args, **kwargs):
        self.event_type = event_type
        self.event_id = 0
        self.delay = 1

        if content_type is None:
            content_type = 'text/event-stream'
        self.streaming_content = streaming_content
        self.streaming_ait = self.streaming_content.__aiter__()
        super().__init__(content_type=content_type, *args, **kwargs)

    def __aiter__(self):
        return self

    async def __anext__(self):
        self.event_id += 1
        if self.event_id == 1:
            return self.make_bytes(self.sse_event(event_type="start-stream", data=''))

        message = await self.streaming_ait.__anext__()
        if message:
            return self.make_bytes(self.sse_event(event_type=self.event_type, data=message))
        return self.make_bytes(self.sse_event(event_type='keep-alive', data=message))
