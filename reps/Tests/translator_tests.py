import unittest
from ..inspector import RaceTranslator

class TranslatorTestCase(unittest.TestCase):
    def setUp(self):
        self.translator = RaceTranslator()

    def test_english(self):
        race = self.translator.translate('Protoss')
        self.assertTrue(race == 'Protoss')

        race = self.translator.translate('Terran')
        self.assertTrue(race == 'Terran')

        race = self.translator.translate('Zerg')
        self.assertTrue(race == 'Zerg')

    def test_chinese(self):
        race = self.translator.translate('\xe6\x98\x9f\xe7\x81\xb5')
        self.assertTrue(race == 'Protoss')

        race = self.translator.translate('\xe4\xba\xba\xe7\xb1\xbb')
        self.assertTrue(race == 'Terran')

        race = self.translator.translate('\xe5\xbc\x82\xe8\x99\xab')
        self.assertTrue(race == 'Zerg')

    def test_korean(self):
        race = self.translator.translate('\xed\x94\x84\xeb\xa1\x9c\xed\x86\xa0\xec\x8a\xa4')
        self.assertTrue(race == 'Protoss')

        race = self.translator.translate('\xed\x85\x8c\xeb\x9e\x80')
        self.assertTrue(race == 'Terran')

        race = self.translator.translate('\xec\xa0\x80\xea\xb7\xb8')
        self.assertTrue(race == 'Zerg')
