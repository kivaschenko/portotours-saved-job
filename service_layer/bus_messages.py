from typing import Type

from service_layer import events, services

base_event = Type[events.Event]


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


# New Product created
def do_something(event: base_event):
    pass



HANDLERS = {
    events.NewProductCreated: [do_something,],
}
