import requests
import re
import base64


TASK_BASE_URL = "http://15.206.47.5:9090"
TASK_URL = f"{TASK_BASE_URL}/task"
SUBMIT_URL = f"{TASK_BASE_URL}/submit"


TASK_SESSION_COOKIE = "REPLACE_ME_WITH_SESSION_COOKIE"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
}


def extract_input_string(html: str) -> str:
    """
    Extracts the random string from the HTML snippet:
    <p>Here is the input string: TqKtYOGXrgGj</p>
    """
    m = re.search(r"Here is the input string:\s*([A-Za-z0-9+/=]+)", html)
    if not m:
        raise ValueError("Could not find input string in HTML")
    return m.group(1).strip()


def build_payload(s: str) -> str:
    """
    Reverse string, base64 encode the reversed string, wrap as:
    CSK__{{payload}}__2025
    """
    reversed_s = s[::-1]
    b64 = base64.b64encode(reversed_s.encode()).decode()
    return f"CSK__{b64}__2025"


def solve_once(session: requests.Session) -> str:
    """
    Fetches a task, builds the payload, submits it, and returns the server response text.
    """
    # 1) Get task
    r = session.get(TASK_URL, timeout=1)
    text = r.text

    if "No active task" in text:
        # The server says there's no task yet
        return "No active task from server."

    # 2) Extract random string from HTML
    input_str = extract_input_string(text)

    # 3) Build final payload
    final_answer = build_payload(input_str)

    # 4) POST to /submit as raw text
    submit_headers = {
        "User-Agent": HEADERS["User-Agent"],
        "Content-Type": "text/plain",
    }

    r2 = session.post(
        SUBMIT_URL,
        data=final_answer,
        headers=submit_headers,
        timeout=1,
    )
    return r2.text


def main():
    # Use a persistent session so cookies + connection are reused
    with requests.Session() as s:
        s.headers.update(HEADERS)

        # Set the session cookie for the task server
        s.cookies.set("session", TASK_SESSION_COOKIE, domain="15.206.47.5")

        while True:
            try:
                resp = solve_once(s)
                print("[*] Server response:", resp)

                if "Too slow" in resp:
                    # Immediately request a new task and try again
                    continue
                elif "No active task" in resp:
                    # You may need to hit /task manually once in browser or wait
                    continue
                else:
                    # Likely got the flag or success message, stop loop
                    break

            except Exception as e:
                print("[!] Error:", e)
                break


if __name__ == "__main__":
    main()
