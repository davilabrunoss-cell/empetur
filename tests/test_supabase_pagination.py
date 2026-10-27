import unittest
from unittest.mock import patch

import httpx

from backend import app


class SupabasePaginationTests(unittest.TestCase):
    def test_validated_events_form_is_enabled_by_default(self):
        disabled = app.parse_disabled_forms(None)
        self.assertEqual(len(disabled), 1)
        self.assertNotIn(app.normalize_questionario_name("Empresas Organizadoras de Eventos"), disabled)

    def test_events_form_is_included_in_automatic_sync(self):
        settings = {
            "ipesquisa_disabled_forms": app.parse_disabled_forms(None),
            "ipesquisa_form_map": {
                "Empresas Organizadoras de Eventos": 8920,
                "Sistema Marítimo e Fluvial": 8933,
            },
        }
        with patch.object(app, "get_settings", return_value=settings):
            forms = app.build_sync_forms([])

        self.assertEqual([(form.questionario, form.codigo_pesquisa) for form in forms], [
            ("Empresas Organizadoras de Eventos", 8920),
        ])

    def test_reads_all_base_rows_across_pages(self):
        real_client = httpx.Client
        source = [{"codigo_pesquisa": "8919", "nro_identificacao": str(index)} for index in range(1399)]
        offsets = []

        def handle(request):
            offset = int(request.url.params["offset"])
            limit = int(request.url.params["limit"])
            self.assertTrue(request.url.params["order"].endswith(",id.asc"))
            offsets.append(offset)
            return httpx.Response(200, json=source[offset : offset + limit])

        with patch.object(app, "build_supabase_base_url", return_value="https://example.test/rest/v1/base"), patch.object(
            app, "build_supabase_headers", return_value={}
        ), patch.object(app.httpx, "Client", side_effect=lambda **kwargs: real_client(transport=httpx.MockTransport(handle))):
            rows = app.read_base_rows_from_supabase()

        self.assertEqual(len(rows), 1399)
        self.assertEqual(rows[-1]["nro_identificacao"], "1398")
        self.assertEqual(offsets, [0, 500, 1000])

    def test_reads_all_previstos_for_summary_and_municipio(self):
        real_client = httpx.Client
        source = [
            {"municipio_slug": "recife", "municipio": "Recife", "atrativo": str(index)}
            for index in range(1101)
        ]

        def handle(request):
            offset = int(request.url.params["offset"])
            limit = int(request.url.params["limit"])
            return httpx.Response(200, json=source[offset : offset + limit])

        with patch.object(app, "build_supabase_previstos_url", return_value="https://example.test/rest/v1/previstos"), patch.object(
            app, "build_supabase_headers", return_value={}
        ), patch.object(app.httpx, "Client", side_effect=lambda **kwargs: real_client(transport=httpx.MockTransport(handle))):
            summary = app.read_previstos_summary_supabase()
            rows = app.read_previstos_by_municipio_supabase("recife")

        self.assertEqual(summary["total_previstos"], 1101)
        self.assertEqual(len(rows), 1101)

    def test_exact_page_multiple_fetches_final_empty_page(self):
        real_client = httpx.Client
        source = [{"municipio_slug": "recife"} for _ in range(1000)]
        offsets = []

        def handle(request):
            offset = int(request.url.params["offset"])
            limit = int(request.url.params["limit"])
            offsets.append(offset)
            return httpx.Response(200, json=source[offset : offset + limit])

        with patch.object(app, "build_supabase_headers", return_value={}), patch.object(
            app.httpx, "Client", side_effect=lambda **kwargs: real_client(transport=httpx.MockTransport(handle))
        ):
            rows = app.read_all_supabase_rows("https://example.test/rest/v1/base", {"select": "municipio_slug"}, "base")

        self.assertEqual(len(rows), 1000)
        self.assertEqual(offsets, [0, 500, 1000])


if __name__ == "__main__":
    unittest.main()
