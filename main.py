
import time
import requests


# ==========================================
# 1. OFFSET PAGINATION
# ==========================================

def offset_pagination():

    base_url = "https://jsonplaceholder.typicode.com/posts"

    page = 1
    limit = 20
    all_posts = []

    while True:

        params = {
            "_page": page,
            "_limit": limit
        }

        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        posts = response.json()

        if not posts:
            break

        all_posts.extend(posts)

        print(f"Page {page}: fetched {len(posts)} posts")

        page += 1

    print(
        f"\nOffset: fetched {len(all_posts)} posts "
        f"in {page - 1} pages"
    )

    return all_posts


# ==========================================
# 2. CURSOR PAGINATION
# ==========================================

def cursor_pagination():

    base_url = "http://127.0.0.1:8001/items"

    cursor = 0
    all_items = []
    calls = 0

    while True:

        params = {
            "cursor": cursor,
            "limit": 15
        }

        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        items = data["items"]
        next_cursor = data["next_cursor"]

        all_items.extend(items)
        calls += 1

        print(f"Call {calls}: fetched {len(items)} items")

        if next_cursor is None:
            break

        cursor = next_cursor

    print(
        f"\nCursor: fetched {len(all_items)} items "
        f"in {calls} calls"
    )

    return all_items


# ==========================================
# 3. GITHUB RATE LIMIT
# ==========================================

def check_github_rate_limit():

    url = "https://api.github.com/rate_limit"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    remaining = response.headers.get(
        "X-RateLimit-Remaining"
    )

    print(f"\nRate limit remaining: {remaining}")

    return remaining


# ==========================================
# 4. SAFE GET WITH RATE LIMIT HANDLING
# ==========================================

def safe_get(url):

    while True:

        response = requests.get(url, timeout=30)

        remaining = response.headers.get(
            "X-RateLimit-Remaining"
        )

        reset_time = response.headers.get(
            "X-RateLimit-Reset"
        )

        if remaining is not None and int(remaining) == 0:

            if reset_time is None:
                raise RuntimeError("Rate limit reset time is missing")

            wait_time = max(
                0,
                int(reset_time) - int(time.time())
            )

            if wait_time > 0:

                print(
                    f"Rate limit exceeded. "
                    f"Sleeping for {wait_time} seconds..."
                )

                time.sleep(wait_time)

            continue

        response.raise_for_status()

        return response


# ==========================================
# 5. TEST SAFE GET
# ==========================================

def test_safe_get():

    url = "https://api.github.com/rate_limit"

    response = safe_get(url)

    remaining = response.headers.get(
        "X-RateLimit-Remaining"
    )

    print(f"safe_get remaining: {remaining}")


# ==========================================
# 6. BONUS: REUSABLE API CLIENT CLASS
# ==========================================

class ApiClient:

    def __init__(self):

        self.session = requests.Session()

    # Safe GET with rate-limit handling
    def safe_get(self, url, params=None):

        while True:

            response = self.session.get(
                url,
                params=params,
                timeout=30
            )

            remaining = response.headers.get(
                "X-RateLimit-Remaining"
            )

            reset_time = response.headers.get(
                "X-RateLimit-Reset"
            )

            if remaining is not None and int(remaining) == 0:

                if reset_time is None:
                    raise RuntimeError("Rate limit reset time is missing")

                wait_time = max(
                    0,
                    int(reset_time) - int(time.time())
                )

                if wait_time > 0:

                    print(
                        f"Rate limit exceeded. "
                        f"Sleeping for {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                continue

            response.raise_for_status()

            return response

    # Offset pagination
    def offset_pagination(self, url, limit=20):

        page = 1
        all_items = []

        while True:

            params = {
                "_page": page,
                "_limit": limit
            }

            response = self.safe_get(url, params=params)

            items = response.json()

            if not items:
                break

            all_items.extend(items)
            page += 1

        print(
            f"Offset: fetched {len(all_items)} items "
            f"in {page - 1} pages"
        )

        return all_items

    # Cursor pagination
    def cursor_pagination(self, url, limit=15):

        cursor = 0
        all_items = []
        calls = 0

        while True:

            params = {
                "cursor": cursor,
                "limit": limit
            }

            response = self.safe_get(url, params=params)

            data = response.json()

            items = data["items"]
            next_cursor = data["next_cursor"]

            all_items.extend(items)
            calls += 1

            if next_cursor is None:
                break

            cursor = next_cursor

        print(
            f"Cursor: fetched {len(all_items)} items "
            f"in {calls} calls"
        )

        return all_items

    # GitHub rate-limit information
    def check_rate_limit(self):

        url = "https://api.github.com/rate_limit"

        response = self.safe_get(url)

        remaining = response.headers.get(
            "X-RateLimit-Remaining"
        )

        print(f"Rate limit remaining: {remaining}")

        return remaining


# ==========================================
# 7. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    print("\n========== BASIC FUNCTIONS ==========\n")

    offset_pagination()

    print("\n----------------------\n")

    cursor_pagination()

    print("\n----------------------\n")

    check_github_rate_limit()

    print("\n----------------------\n")

    test_safe_get()

    print("\n========== BONUS API CLIENT ==========\n")

    client = ApiClient()

    client.offset_pagination(
        "https://jsonplaceholder.typicode.com/posts"
    )

    client.cursor_pagination(
        "http://127.0.0.1:8001/items"
    )

    client.check_rate_limit()
