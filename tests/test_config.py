import unittest
import os

os.environ["MONGO_URI"] = ""
os.environ["MONGODB_URI"] = ""
import backend.main as api


class ConfigTests(unittest.TestCase):
    def test_default_cors_origins_include_local_and_split_vercel_apps(self):
        self.assertIn("http://localhost:5177", api.CORS_ORIGINS)
        self.assertIn("http://127.0.0.1:5177", api.CORS_ORIGINS)
        self.assertIn("https://pyam-patient.vercel.app", api.CORS_ORIGINS)
        self.assertIn("https://pyam-staff.vercel.app", api.CORS_ORIGINS)


if __name__ == "__main__":
    unittest.main()
