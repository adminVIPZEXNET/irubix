import unittest
from irubix.shad import Shad, ShadAuthError

class ShadNativeTests(unittest.TestCase):
 def test_platform_validation(self):
  with self.assertRaises(ValueError): Shad(auth="a"*32,private_key="invalid",platform="unknown")
 def test_auth_required(self):
  with self.assertRaises(ShadAuthError): Shad()
 def test_invalid_auth_rejected(self):
  with self.assertRaises(ShadAuthError): Shad(auth="invalid",private_key="invalid")
 def test_public_aliases(self):
  from irubix import shad
  self.assertIs(shad.Shad,shad.Client); self.assertIs(shad.Shad,shad.Messenger)
  self.assertTrue(callable(shad.Shad.on_new_message))
if __name__=="__main__": unittest.main()
