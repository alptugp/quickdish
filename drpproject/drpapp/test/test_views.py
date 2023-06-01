from django.test import TestCase

# All test functions should start with "test_" to be recognized by Django
# All test files should be named "test_*.py" to be recognized by Django
class ProductLinkTestCase(TestCase):
    # Dummy test to check if tests are working
    def test_dummy(self):
        self.assertEqual(1, 1)