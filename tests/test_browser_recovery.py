"""Regression tests for stale browser/CDP recovery."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server  # noqa: E402


class DeadTransportTest(unittest.TestCase):
    def test_stale_cdp_target_is_dead(self):
        self.assertTrue(server._is_dead_transport(
            RuntimeError("No target with given id found [code: -32602]")
        ))

    def test_missing_cdp_session_is_dead(self):
        self.assertTrue(server._is_dead_transport(
            RuntimeError("Session with given id not found")
        ))

    def test_ordinary_provider_error_is_not_dead(self):
        self.assertFalse(server._is_dead_transport(
            RuntimeError("provider did not return an image")
        ))


if __name__ == "__main__":
    unittest.main()
