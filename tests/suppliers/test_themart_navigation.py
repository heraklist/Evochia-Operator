import unittest
from pathlib import Path
import sys


PROVIDER = Path(__file__).resolve().parents[2] / "scripts/supplier-providers/themart"
sys.path.insert(0, str(PROVIDER))

from themart_capture import navigate_with_retry


class FakePage:
    def __init__(self):
        self.goto_calls = 0
        self.waits = []

    async def goto(self, url, wait_until, timeout):
        self.goto_calls += 1
        if self.goto_calls == 1:
            raise Exception(
                'Page.goto: Navigation to "https://example.test/category" '
                'is interrupted by another navigation to "https://example.test/"'
            )
        return None

    async def wait_for_load_state(self, state, timeout):
        self.waits.append((state, timeout))

    async def wait_for_timeout(self, timeout):
        self.waits.append(("timeout", timeout))


class NavigationTests(unittest.IsolatedAsyncioTestCase):
    async def test_navigate_with_retry_recovers_from_interrupted_navigation(self):
        page = FakePage()

        await navigate_with_retry(page, "https://example.test/category", retries=2)

        self.assertEqual(page.goto_calls, 2)
        self.assertIn(("timeout", 1500), page.waits)


if __name__ == "__main__":
    unittest.main()
