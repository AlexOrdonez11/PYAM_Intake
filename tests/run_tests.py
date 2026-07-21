import os
import sys
import unittest
from pathlib import Path


os.environ["MONGO_URI"] = ""
os.environ["MONGODB_URI"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
