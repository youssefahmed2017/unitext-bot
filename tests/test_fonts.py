import unittest

from unitext.fonts import normalize_style, style_names, transform


class FontTests(unittest.TestCase):
    def test_all_styles_return_text(self) -> None:
        for style in style_names():
            result = transform("Hello 123!", style)
            self.assertIsInstance(result, str)
            self.assertTrue(result)

    def test_bold(self) -> None:
        self.assertEqual(transform("Hello", "bold"), "𝐇𝐞𝐥𝐥𝐨")

    def test_double_alias(self) -> None:
        self.assertEqual(normalize_style("double-struck"), "double")
        self.assertEqual(transform("ABC", "double_struck"), "𝔸𝔹ℂ")

    def test_punctuation_is_preserved(self) -> None:
        self.assertEqual(transform("Hello, world! #42", "bold"), "𝐇𝐞𝐥𝐥𝐨, 𝐰𝐨𝐫𝐥𝐝! #𝟒𝟐")

    def test_unknown_style(self) -> None:
        self.assertIsNone(normalize_style("not_a_real_font"))
        with self.assertRaises(ValueError):
            transform("Hello", "not_a_real_font")


if __name__ == "__main__":
    unittest.main()
