"""Barebones pub/sub mechanism"""

import asyncio
from fastapi import Request


class EVENTS:
    CREATE_SPACECRAFT = "create_spacecraft"
    DELETE_SPACECRAFT = "delete_spacecraft"
    REPAIR_SPACECRAFT = "repair_spacecraft"
    RANDOM_MALFUNCTION = "random_malfunction"


class _PubSub:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type):
        if event_type in self.subscribers:
            event_data = {"type": event_type}
            for callback in self.subscribers[event_type]:
                callback(event_data)

    def unsubscribe(self, event_type, callback):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
            if not self.subscribers[event_type]:  # Clean up if no subscribers left
                del self.subscribers[event_type]


PubSub = _PubSub()


# Simple system using async queues to handle events
async def sse_events_handler(request: Request):
    queue = asyncio.Queue()
    new_message_event = asyncio.Event()

    def add_message_to_queue(event_data):
        formatted_data = f"event: {event_data['type']}\ndata: \n\n"  # Don't even need to send data for now
        queue.put_nowait(formatted_data)
        new_message_event.set()

    # Subscribe to events
    PubSub.subscribe(EVENTS.CREATE_SPACECRAFT, add_message_to_queue)
    PubSub.subscribe(EVENTS.DELETE_SPACECRAFT, add_message_to_queue)
    PubSub.subscribe(EVENTS.REPAIR_SPACECRAFT, add_message_to_queue)
    PubSub.subscribe(EVENTS.RANDOM_MALFUNCTION, add_message_to_queue)
    try:
        while True:
            if await request.is_disconnected():
                break
            if not queue.empty():
                yield await queue.get()
                new_message_event.clear()
            else:
                await new_message_event.wait()
    finally:
        # Cleanup: unsubscribe from pubsub on connection close
        PubSub.unsubscribe(EVENTS.CREATE_SPACECRAFT, add_message_to_queue)
        PubSub.unsubscribe(EVENTS.DELETE_SPACECRAFT, add_message_to_queue)
        PubSub.unsubscribe(EVENTS.REPAIR_SPACECRAFT, add_message_to_queue)
        PubSub.unsubscribe(EVENTS.RANDOM_MALFUNCTION, add_message_to_queue)
