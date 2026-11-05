import httpx


def fetch_url(url, output_path):
    headers = {
        "User-Agent": "GG-Job-Scraper/1.0"
    }

    try:
        r = httpx.get(
            url=url,
            timeout=10.0,
            headers=headers
        )

        r.raise_for_status()
        print("Request successful")

        print("Status:", r.status_code)
        print("Content-Type:", r.headers.get("Content-Type"))
        print("Response size:", len(r.content))

        with open(output_path, "wb") as write_file:
            write_file.write(r.content)

        print("Page saved successfully.")

    except httpx.HTTPStatusError as error:
        print("HTTP error:", error)

    except httpx.RequestError as error:
        print("Request error:", error)

    finally:
        print("HTTP request finished.")


if __name__ == "__main__":
    fetch_url(
        "https://www.example.com",
        "data/raw/response.html"
    )