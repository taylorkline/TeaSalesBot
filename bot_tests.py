import bot
import unittest

class TestBot(unittest.TestCase):
    def setUp(self):
        self.vendors = bot.load_vendors()

    def test_name_present(self):
        mentions = bot.get_vendors_mentioned("like What-Cha like", self.vendors)
        self.assertTrue(mentions)

    def test_name_present_casing(self):
        mentions = bot.get_vendors_mentioned("like wHat-Cha like", self.vendors)
        self.assertTrue(mentions)

    def test_name_present_yunnan_sourcing(self):
        mentions = bot.get_vendors_mentioned("like yunnan sourcing like", self.vendors)
        self.assertTrue(mentions)

    def test_exact_name_not_present_yunnan_sourcing(self):
        mentions = bot.get_vendors_mentioned("like yunnan-sourcing like", self.vendors)
        self.assertFalse(mentions)

    def test_username_present(self):
        mentions = bot.get_vendors_mentioned("like /u/yunnanSourcing like", self.vendors)
        self.assertTrue(mentions)

    def test_username_not_present(self):
        mentions = bot.get_vendors_mentioned("like /u/yunnanSourcin like", self.vendors)
        self.assertFalse(mentions)

    def test_url_present(self):
        mentions = bot.get_vendors_mentioned("like https://yunnanSourcing.com like", self.vendors)
        self.assertTrue(mentions)

    def test_nickname_present(self):
        mentions = bot.get_vendors_mentioned("like whatCHA like", self.vendors)
        self.assertTrue(mentions)

    def test_nickname_present_punctuation(self):
        mentions = bot.get_vendors_mentioned("like whatCHA's like", self.vendors)
        self.assertTrue(mentions)

    def test_multiple_mentions(self):
        t = "like WhatCha or Yunnan Sourcing or Yunomi?"
        mentions = bot.get_vendors_mentioned(t, self.vendors)
        self.assertTrue(len(mentions) == 3)

    def test_duplicate_mentions(self):
        t = "like WhatCha or whatcha or what-cha or what-cha.com?"
        mentions = bot.get_vendors_mentioned(t, self.vendors)
        self.assertTrue(len(mentions) == 1)

if __name__ == "__main__":
    unittest.main()
