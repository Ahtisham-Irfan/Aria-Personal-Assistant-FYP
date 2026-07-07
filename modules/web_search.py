from PySide6.QtCore import QThread, Signal


class _SearchThread(QThread):
    result_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.query = query

    def run(self):
        try:
            import requests
        except ImportError:
            self.error_occurred.emit(
                "Please install requests: pip install requests"
            )
            return

        query = self.query.strip()
        if not query:
            self.error_occurred.emit("What would you like me to search for?")
            return

        try:
            # Wikipedia REST summary API — no API key required
            url = (
                "https://en.wikipedia.org/api/rest_v1/page/summary/"
                + requests.utils.quote(query)
            )
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get("extract", "").strip()
                if extract:
                    self.result_ready.emit(extract)
                    return
        except Exception as e:
            print(f"Wikipedia search error: {e}")

        try:
            # Fallback: DuckDuckGo Instant Answer API
            resp = requests.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query, "format": "json",
                    "no_redirect": 1, "no_html": 1
                },
                timeout=6
            )
            data = resp.json()
            text = (
                data.get("AbstractText")
                or data.get("Answer")
                or ""
            ).strip()
            if text:
                self.result_ready.emit(text)
                return
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")

        self.error_occurred.emit(
            f"Sorry, I could not find information about '{query}'."
        )


class WebSearchEngine:
    """
    Simple threaded web-lookup using free, keyless APIs
    (Wikipedia summary + DuckDuckGo instant answers).
    """

    def __init__(self):
        self._thread = None

    def search(self, query, on_result=None, on_error=None):
        self.stop()
        self._thread = _SearchThread(query)
        if on_result:
            self._thread.result_ready.connect(on_result)
        if on_error:
            self._thread.error_occurred.connect(on_error)
        self._thread.start()

    def stop(self):
        if self._thread and self._thread.isRunning():
            self._thread.terminate()
            self._thread.wait(200)
        self._thread = None
