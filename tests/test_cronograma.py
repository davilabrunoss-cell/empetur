import hashlib
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend import app as backend


class CronogramaTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(backend.app)
        self.token = "a" * 64
        self.headers = {"X-Cronograma-Token": self.token}

    def test_catalog_limits_municipality_and_code(self):
        backend.validate_cronograma_target("afranio", "A1-0026")
        for slug, code in [("afranio", "B2-0052"), ("bodoco", "A1-0026"), ("unknown", None)]:
            with self.assertRaises(backend.HTTPException) as error:
                backend.validate_cronograma_target(slug, code)
            self.assertEqual(error.exception.status_code, 404)

    def test_token_is_scoped_to_municipality(self):
        with patch.object(backend, "read_cronograma_token_hash", side_effect=lambda slug: (
            hashlib.sha256(self.token.encode()).hexdigest() if slug == "afranio" else None
        )):
            self.assertTrue(backend.can_edit_cronograma("afranio", self.token))
            self.assertFalse(backend.can_edit_cronograma("bodoco", self.token))
            self.assertFalse(backend.can_edit_cronograma("afranio", "short"))

    def test_public_read_and_only_date_write(self):
        with patch.object(backend, "has_supabase_status_backend", return_value=True), patch.object(
            backend, "read_cronograma", return_value={"A1-0026": "2026-11-12"}
        ), patch.object(backend, "can_edit_cronograma", side_effect=lambda slug, token: token == self.token), patch.object(
            backend, "save_cronograma", return_value={"codigo": "A1-0026", "data_visita": "2026-11-13"}
        ) as save:
            public = self.client.get("/api/cronograma/afranio")
            self.assertEqual(public.status_code, 200)
            self.assertFalse(public.json()["pode_editar"])
            self.assertEqual(public.json()["datas"]["A1-0026"], "2026-11-12")

            self.assertEqual(self.client.put(
                "/api/cronograma/afranio/A1-0026", json={"data_visita": "2026-11-13"}
            ).status_code, 403)
            self.assertEqual(self.client.put(
                "/api/cronograma/afranio/A1-0026", headers=self.headers,
                json={"data_visita": "2026-11-13", "observacao": "alterada"}
            ).status_code, 422)
            self.assertEqual(self.client.put(
                "/api/cronograma/afranio/B2-0052", headers=self.headers,
                json={"data_visita": "2026-11-13"}
            ).status_code, 404)
            saved = self.client.put(
                "/api/cronograma/afranio/A1-0026", headers=self.headers,
                json={"data_visita": "2026-11-13"}
            )
            self.assertEqual(saved.status_code, 200)
            save.assert_called_once()
            self.assertEqual(str(save.call_args.args[2]), "2026-11-13")


if __name__ == "__main__":
    unittest.main()
