
from fastapi import FastAPI

app = FastAPI()

# Mock database containing 45 items
items = [
    {"id": i, "name": f"Item {i}"}
    for i in range(1, 46)
]


@app.get("/items")
def get_items(cursor: int = 0, limit: int = 15):

    start = cursor
    end = start + limit

    results = items[start:end]

    if end < len(items):
        next_cursor = end
    else:
        next_cursor = None

    return {
        "items": results,
        "next_cursor": next_cursor
    }
