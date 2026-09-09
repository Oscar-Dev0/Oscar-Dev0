from datetime import date
import unittest
from update_age import age_on, update_content


class AgeTests(unittest.TestCase):
    def test_birthday_boundary(self):
        self.assertEqual(age_on(date(2027, 1, 4)), 22)
        self.assertEqual(age_on(date(2027, 1, 5)), 23)
        self.assertEqual(age_on(date(2027, 1, 6)), 23)

    def test_only_age_changes_and_second_run_is_stable(self):
        source = "Intro 2026 <!-- AGE:START -->20<!-- AGE:END --> final"
        result = update_content(source, date(2026, 9, 9))
        self.assertEqual(result, source.replace("-->20<!--", "-->22<!--"))
        self.assertEqual(update_content(result, date(2026, 9, 9)), result)

    def test_missing_or_duplicate_blocks_fail(self):
        for content in ("No age", "<!-- AGE:START -->22<!-- AGE:END -->" * 2):
            with self.assertRaises(ValueError):
                update_content(content, date(2026, 9, 9))


if __name__ == "__main__":
    unittest.main()
