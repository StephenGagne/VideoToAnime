import os
import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__))

    runner = unittest.TextTestRunner()
    runner.run(suite)