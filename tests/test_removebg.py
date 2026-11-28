"""Offline regression tests: python -m unittest discover -s tests -v."""

import asyncio
import base64
import importlib.util
import io
import os
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch

import aiohttp
from aiohttp import web
from aiohttp.test_utils import TestServer
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def load_module():
    utils = ModuleType("utils")
    utils.modules_help = {}
    utils.prefix = "."
    config = ModuleType("utils.config")
    config.leonardo_key = "test-key"
    scripts = ModuleType("utils.scripts")
    scripts.edit_or_reply = AsyncMock()
    scripts.format_exc = str
    spec = importlib.util.spec_from_file_location(
        "removebg_under_test", ROOT / "modules/removebg.py"
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict(
        "sys.modules",
        {"utils": utils, "utils.config": config, "utils.scripts": scripts},
    ):
        spec.loader.exec_module(module)
    return module


removebg = load_module()
LEONARDO_URL = removebg.LEONARDO_URL
LEONARDO_TIMEOUT = removebg.LEONARDO_TIMEOUT
PNG_BUFFER = io.BytesIO()
Image.new("RGBA", (2, 2), (255, 0, 0, 128)).save(PNG_BUFFER, format="PNG")
PNG = PNG_BUFFER.getvalue()


class LeonardoTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.status = 200
        self.delay = 0
        self.download_status = 200
        self.download_body = PNG
        self.posts = []
        self.gets = []
        app = web.Application()
        app.router.add_post("/generate", self.generate)
        app.router.add_get("/result", self.download)
        server = TestServer(app)
        await server.start_server()
        self.addAsyncCleanup(server.close)
        self.body = {"results": [{"url": str(server.make_url("/result"))}]}
        url_patch = patch.object(
            removebg, "LEONARDO_URL", str(server.make_url("/generate"))
        )
        url_patch.start()
        self.addCleanup(url_patch.stop)

    async def generate(self, request):
        self.posts.append((dict(request.headers), await request.json()))
        await asyncio.sleep(self.delay)
        if isinstance(self.body, str):
            return web.Response(status=self.status, text=self.body)
        return web.json_response(self.body, status=self.status)

    async def download(self, request):
        self.gets.append(dict(request.headers))
        return web.Response(
            status=self.download_status,
            body=self.download_body,
            headers={"Content-Type": "image/png"},
        )

    def test_endpoint_and_timeout_follow_the_docs(self):
        self.assertEqual(
            LEONARDO_URL, "https://cloud.leonardo.ai/api/rest/v2/generationssync"
        )
        self.assertGreater(LEONARDO_TIMEOUT.total, 27)

    async def test_success_request_and_download(self):
        self.assertEqual(await removebg.leonardo_remove_bg(PNG), (PNG, None))
        headers, body = self.posts[0]
        self.assertEqual(headers["Authorization"], "Bearer test-key")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(set(body), {"model", "ephemeral", "parameters"})
        self.assertEqual(set(body["parameters"]), {"size", "format", "guidances"})
        self.assertEqual(body["model"], "remove-bg")
        self.assertIs(body["ephemeral"], True)
        self.assertEqual(body["parameters"]["size"], "auto")
        self.assertEqual(body["parameters"]["format"], "png")
        reference = body["parameters"]["guidances"]["image_reference"]
        self.assertEqual(len(reference), 1)
        self.assertEqual(reference[0]["image"]["type"], "BASE64")
        self.assertEqual(base64.b64decode(reference[0]["image"]["data"]), PNG)
        self.assertNotIn("Authorization", self.gets[0])

    async def test_http_errors_never_download_even_with_results(self):
        for status in (401, 429, 500):
            with self.subTest(status=status):
                self.status = status
                data, error = await removebg.leonardo_remove_bg(PNG)
                self.assertIsNone(data)
                self.assertIn(str(status), error)
        self.assertEqual(self.gets, [])

    async def test_http_200_errors_take_precedence_over_results(self):
        self.body["errors"] = [
            {"message": "Invalid API key", "extensions": {"code": "UNAUTHENTICATED"}}
        ]
        data, error = await removebg.leonardo_remove_bg(PNG)
        self.assertIsNone(data)
        self.assertIn("Invalid API key", error)
        self.assertEqual(self.gets, [])

    async def test_invalid_response_shapes_do_not_raise(self):
        for body in (
            None,
            [],
            "not json",
            {},
            {"errors": []},
            {"results": []},
            {"results": {}},
            {"results": "bad"},
            {"results": [None]},
            {"results": ["bad"]},
            {"results": [{}]},
            {"results": [{"url": 123}]},
            {"results": [{"url": ""}]},
        ):
            with self.subTest(body=body):
                self.body = body
                data, error = await removebg.leonardo_remove_bg(PNG)
                self.assertIsNone(data)
                self.assertTrue(error)
        self.assertEqual(self.gets, [])

    async def test_moderated_empty_result(self):
        self.body = {"blockedCount": 1, "results": []}
        data, error = await removebg.leonardo_remove_bg(PNG)
        self.assertIsNone(data)
        self.assertIn("blocked", error.lower())

    async def test_non_json_http_error_preserves_status_and_detail(self):
        self.status = 502
        self.body = "upstream unavailable"
        data, error = await removebg.leonardo_remove_bg(PNG)
        self.assertIsNone(data)
        self.assertIn("502", error)
        self.assertIn("upstream unavailable", error)

    async def test_failed_download(self):
        self.download_status = 403
        data, error = await removebg.leonardo_remove_bg(PNG)
        self.assertIsNone(data)
        self.assertIn("403", error)

    async def test_invalid_or_empty_image_is_failure(self):
        for content in (b"", b'{"error": "expired"}'):
            with self.subTest(content=content):
                self.download_body = content
                data, error = await removebg.leonardo_remove_bg(PNG)
                self.assertIsNone(data)
                self.assertTrue(error)

    async def test_empty_input_never_calls_provider(self):
        data, error = await removebg.leonardo_remove_bg(b"")
        self.assertIsNone(data)
        self.assertTrue(error)
        self.assertEqual(self.posts, [])

    async def test_transport_failures_are_returned(self):
        for method in ("post", "get"):
            for error in (
                aiohttp.ClientConnectionError("connection lost"),
                asyncio.TimeoutError(),
            ):
                with self.subTest(
                    method=method, error=type(error).__name__
                ), patch.object(aiohttp.ClientSession, method, side_effect=error):
                    data, detail = await removebg.leonardo_remove_bg(PNG)
                    self.assertIsNone(data)
                    self.assertTrue(detail)

    async def test_slow_response_times_out(self):
        self.delay = 0.5
        with patch.object(
            removebg, "LEONARDO_TIMEOUT", aiohttp.ClientTimeout(total=0.1)
        ):
            data, error = await removebg.leonardo_remove_bg(PNG)
        self.assertIsNone(data)
        self.assertIn("timed out", error)

    async def test_cancellation_propagates(self):
        with patch.object(
            aiohttp.ClientSession, "post", side_effect=asyncio.CancelledError()
        ), self.assertRaises(asyncio.CancelledError):
            await removebg.leonardo_remove_bg(PNG)


class CommandTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.directory, ignore_errors=True)
        self.photo = self.directory / "photo.png"
        self.photo.write_bytes(PNG)
        self.message = SimpleNamespace(
            chat=SimpleNamespace(id=123),
            id=456,
            reply_to_message=SimpleNamespace(
                download=AsyncMock(return_value=str(self.photo))
            ),
            download=AsyncMock(side_effect=ValueError("No media")),
            edit=AsyncMock(),
            edit_text=AsyncMock(),
            delete=AsyncMock(),
            reply_text=AsyncMock(),
        )
        self.progress = SimpleNamespace(edit=AsyncMock())
        self.client = SimpleNamespace(send_photo=AsyncMock(), send_document=AsyncMock())
        self.patches = [
            patch.object(removebg, "leonardo_key", "test-key"),
            patch.object(
                removebg, "edit_or_reply", AsyncMock(return_value=self.progress)
            ),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    async def run_rmbg(self, helper):
        with patch.object(
            removebg, "convert_to_image", AsyncMock(return_value=str(self.photo))
        ), patch.object(removebg, "leonardo_remove_bg", helper):
            await removebg.rmbg(self.client, self.message)

    async def test_wrapper_returns_bytesio_or_none(self):
        with patch.object(
            removebg, "leonardo_remove_bg", AsyncMock(return_value=(PNG, None))
        ):
            result = await removebg.remove_background(self.photo)
        self.assertIsInstance(result, io.BytesIO)
        self.assertEqual(result.read(), PNG)
        with patch.object(
            removebg,
            "leonardo_remove_bg",
            AsyncMock(return_value=(None, "Invalid key")),
        ), patch("builtins.print"):
            self.assertIsNone(await removebg.remove_background(self.photo))

    async def test_missing_key_guards_both_commands(self):
        with patch.object(removebg, "leonardo_key", ""), patch.object(
            removebg, "leonardo_remove_bg", AsyncMock()
        ) as helper:
            for command in (removebg.rmbg, removebg.rembg):
                with self.subTest(command=command.__name__):
                    removebg.edit_or_reply.reset_mock()
                    await command(self.client, self.message)
                    self.assertIn(
                        "LEONARDO_API_KEY", removebg.edit_or_reply.call_args.args[1]
                    )
            helper.assert_not_awaited()
        self.message.download.assert_not_awaited()

    async def test_rebg_awaits_helper_and_sends_photo(self):
        with patch.object(
            removebg, "leonardo_remove_bg", AsyncMock(return_value=(PNG, None))
        ) as helper:
            await removebg.rembg(self.client, self.message)
        helper.assert_awaited_once_with(PNG)
        photo = self.client.send_photo.call_args.kwargs["photo"]
        self.assertEqual(photo.getvalue(), PNG)
        self.message.reply_text.assert_not_awaited()
        self.assertFalse(self.photo.exists())

    async def test_rebg_without_reply_or_media(self):
        self.message.reply_to_message = None
        await removebg.rembg(self.client, self.message)
        self.assertIn("File not found", self.message.edit.call_args.args[0])
        self.client.send_photo.assert_not_awaited()
        self.message.reply_text.assert_not_awaited()

    async def test_rebg_failed_download_does_not_mask_error(self):
        self.message.reply_to_message.download.side_effect = ValueError("No media")
        await removebg.rembg(self.client, self.message)
        self.assertIn("File not found", self.message.edit.call_args.args[0])

    async def test_rebg_none_download_is_handled(self):
        self.message.download.side_effect = None
        self.message.download.return_value = None
        await removebg.rembg(self.client, self.message)
        self.assertIn("File not found", self.message.edit.call_args.args[0])
        self.message.reply_text.assert_not_awaited()

    async def test_rebg_provider_error_cleans_input(self):
        with patch.object(
            removebg,
            "leonardo_remove_bg",
            AsyncMock(return_value=(None, "Invalid key")),
        ), patch("builtins.print"):
            await removebg.rembg(self.client, self.message)
        self.message.edit_text.assert_awaited_once()
        self.assertFalse(self.photo.exists())
        self.client.send_photo.assert_not_awaited()

    async def test_rmbg_sends_png_document_and_cleans_input(self):
        async def send_document(_chat_id, document, **_kwargs):
            self.assertEqual(document.read(), PNG)
            self.assertEqual(document.name, "BG_rem.png")

        self.client.send_document.side_effect = send_document
        await self.run_rmbg(AsyncMock(return_value=(PNG, None)))
        self.client.send_document.assert_awaited_once()
        self.assertFalse(self.photo.exists())

    async def test_rmbg_provider_error_is_safe_text(self):
        detail = '<bad> & "error" `test`'
        await self.run_rmbg(AsyncMock(return_value=(None, detail)))
        text = self.progress.edit.call_args.args[0]
        self.assertNotIn("<bad>", text)
        self.assertIn("&lt;bad&gt;", text)
        self.assertFalse(self.photo.exists())

    async def test_rmbg_provider_error_is_truncated(self):
        await self.run_rmbg(AsyncMock(return_value=(None, "x" * 10000)))
        self.assertLess(len(self.progress.edit.call_args.args[0]), 2000)

    async def test_rmbg_cancellation_cleans_input(self):
        with self.assertRaises(asyncio.CancelledError):
            await self.run_rmbg(AsyncMock(side_effect=asyncio.CancelledError()))
        self.assertFalse(self.photo.exists())

    async def test_rmbg_leaves_unrelated_output_file_alone(self):
        previous_output = self.directory / "BG_rem.png"
        previous_output.write_bytes(b"keep this file")
        previous_directory = os.getcwd()
        try:
            os.chdir(self.directory)
            await self.run_rmbg(AsyncMock(return_value=(PNG, None)))
            self.assertEqual(previous_output.read_bytes(), b"keep this file")
        finally:
            os.chdir(previous_directory)


class ConfigTests(unittest.TestCase):
    def test_new_key_is_optional_and_old_key_is_not_forwarded(self):
        config_path = ROOT / "utils/config.py"
        required = {
            "API_ID": "123",
            "API_HASH": "test",
            "STRINGSESSION": "",
            "DATABASE_TYPE": "sqlite3",
            "DATABASE_NAME": "test.db",
            "APIFLASH_KEY": "",
        }
        for keys, expected in (
            ({}, ""),
            ({"RMBG_KEY": "old-key"}, ""),
            ({"LEONARDO_API_KEY": "new-key", "RMBG_KEY": "old-key"}, "new-key"),
        ):
            with self.subTest(keys=keys), tempfile.TemporaryDirectory() as directory:
                previous_directory = os.getcwd()
                try:
                    os.chdir(directory)
                    with patch.dict(os.environ, {**required, **keys}, clear=True):
                        config = runpy.run_path(str(config_path))
                    self.assertEqual(config["leonardo_key"], expected)
                finally:
                    os.chdir(previous_directory)


if __name__ == "__main__":
    unittest.main()
