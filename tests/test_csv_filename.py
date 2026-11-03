import unittest

from empetur_core.consolidacao import extract_questionario


class CsvFilenameTests(unittest.TestCase):
    def test_accepts_original_filename(self):
        self.assertEqual(
            extract_questionario("#1265803711 _ EMPETUR - Atrativos Culturais - 2026.csv"),
            "Atrativos Culturais",
        )

    def test_accepts_coded_filename(self):
        self.assertEqual(
            extract_questionario("A2.1 - #1265803711 _ EMPETUR - Atrativos Culturais - 2026.csv"),
            "Atrativos Culturais",
        )

    def test_accepts_coded_novo_and_windows_suffix(self):
        self.assertEqual(
            extract_questionario("C5 - #1265803711 _ EMPETUR - Sistema Aéreo - NOVO (1).csv"),
            "Sistema Aéreo",
        )

    def test_rejects_other_project(self):
        with self.assertRaises(ValueError):
            extract_questionario("C5 - outro-projeto.csv")


if __name__ == "__main__":
    unittest.main()
