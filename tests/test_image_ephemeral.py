"""Image-generation requests propagate provider-side conversation cleanup."""

import asyncio
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server  # noqa: E402


class ImageEphemeralTest(unittest.TestCase):
    class Provider:
        name = "chatgpt-browser"
        supports_images = True
        supports_upload = True

    def test_request_field_is_opt_in_at_the_http_layer(self):
        self.assertFalse(server.ImageGenRequest(prompt="p").ephemeral)
        self.assertTrue(server.ImageGenRequest(prompt="p", ephemeral=True).ephemeral)

    def test_run_image_request_passes_ephemeral_to_browser_drive(self):
        async def run():
            result_image = {"b64": "aW1hZ2U=", "mime": "image/png"}
            with mock.patch.object(
                server,
                "drive_once",
                new=mock.AsyncMock(return_value=("", [result_image])),
            ) as drive:
                result = await server._run_image_request(
                    self.Provider(),
                    "draw",
                    [],
                    None,
                    "b64_json",
                    allow_local_paths=True,
                    ephemeral=True,
                )
            self.assertEqual(result["data"][0]["b64_json"], "aW1hZ2U=")
            self.assertTrue(drive.await_args.kwargs["ephemeral"])

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
