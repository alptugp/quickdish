from django.test import TestCase

class CICDTestCase(TestCase):
  def test_someTest(self):
    a = 5
    b = 5
    self.assertEquals(a, b)