import unittest


def run_tests():
    test_modules = [
        'tests.domain_entities_tests',
        'tests.storage_tests'
    ]

    suite = unittest.TestSuite()

    for t in test_modules:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(t))

    unittest.TextTestRunner().run(suite)


if __name__ == "tests.run_tests":
    run_tests()
