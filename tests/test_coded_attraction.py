import unittest

from empetur_core.consolidacao import consolidate_csv_rows


class CodedAttractionTests(unittest.TestCase):
    FILE_NAME = "A2.4 - #1265803711 _ EMPETUR - Feiras e Exposições - 2026.csv"
    OLD_NAME = "3. Nome do Atrativo. Informar o nome pelo qual é conhecido."
    NEW_NAME = "Atrativo previsto. Selecione o item da lista do município ou Outro."
    CATEGORY = "1. Tipo da Categoria. Selecionar Feiras e Exposições."

    def consolidate(self, rows):
        return consolidate_csv_rows(self.FILE_NAME, rows, "03/11/2026", "03/11/2026 12:00:00")

    def test_new_selection_takes_precedence_over_old_text(self):
        rows = [
            ["P0. Município", self.CATEGORY, self.OLD_NAME, self.NEW_NAME],
            ["Bodocó", "Feiras e Exposições", "nome escrito", "Feira do Queijo | A2.4-0080"],
        ]
        result = self.consolidate(rows)
        self.assertEqual(result[0]["nome_atrativo"], "Feira do Queijo | A2.4-0080")

    def test_outro_uses_old_text(self):
        rows = [
            ["P0. Município", self.CATEGORY, self.OLD_NAME, self.NEW_NAME],
            ["Exu", "Feiras e Exposições", "Evento local", "Outro atrativo não listado"],
        ]
        self.assertEqual(self.consolidate(rows)[0]["nome_atrativo"], "Evento local")

    def test_historical_export_without_new_column(self):
        rows = [
            ["P0. Município", self.CATEGORY, self.OLD_NAME],
            ["Afrânio", "Feiras e Exposições", "Expoleite Afrânio"],
        ]
        self.assertEqual(self.consolidate(rows)[0]["nome_atrativo"], "Expoleite Afrânio")


if __name__ == "__main__":
    unittest.main()
