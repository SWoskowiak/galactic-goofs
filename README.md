# Galactic Goofs - Oops the sattellites are breaking. Fix Em

This is a FastAPI application that allows you to create spacecraft and get their live status

## Installation

The entire application is dockerized so once you have cloned the repo
    ```
    docker-compose up
    ```
This should download the required container images and copy everything in appropriately and start up the application via the run.sh script.

The app will be running under <http://localhost:8000/>

## Notes

.env is included, normally this is not the case but this is for simplicity of distribution and contains nothing of import as this is not a production app

All connected clients are syncronized so be sure to open a couple tabs and see it working!

## Approach

My Approach to this project was to keep things as simple as possible. My python is rusty currently but wanted to learn some new things and play with fastAPI more.

1. Front end:
    - Use htmx for "reactive" front end components
    - SSE events to handle triggering the htmx data fetching to keep clients in sync with state changes.
    - No state management at all in front-end
2. Back end:
    - FastAPI application + SqlAlchemy/Alembic.
    - No JSON data returns anywhere on routes, state entirely managed via the data returned in the list route in HTML

I also avoided using ORM models in general since I wanted to see how much I can utilize raw commands and sqlAlchemy returns directly.

## Things I would love to add/improve

There are no tests for this project unfortunately so I would add some basic pytest assertions on routes as a starting point.

There is a lot of error handling improvement in general to build upon for route handling.

I would add pydantic model validation on the backend to ensure data integrity on both ends.

No events stored anywhere, the logging is purely just front-end and extremely basic so would create a robust event log

Event synchronization is entirely localized to the app instance, if we wanted to horizontally scale our web server we would need to abstract the pubsub mechanism to something like a shared redis instance.
