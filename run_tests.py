import unittest, io, sys, os
sys.path.insert(0, os.path.dirname(__file__))
loader = unittest.TestLoader()
suite  = loader.discover("tests", pattern="test_*.py")
stream = io.StringIO()
runner = unittest.TextTestRunner(stream=stream, verbosity=2)
result = runner.run(suite)
output = stream.getvalue()
with open("test_results.txt", "w", encoding="utf-8") as f:
    f.write(output)
    f.write(f"\nTests run : {result.testsRun}\n")
    f.write(f"Failures  : {len(result.failures)}\n")
    f.write(f"Errors    : {len(result.errors)}\n")
    if result.wasSuccessful():
        f.write("OVERALL   : ALL TESTS PASSED\n")
    else:
        f.write("OVERALL   : SOME TESTS FAILED\n")
        for test, tb in result.failures + result.errors:
            f.write(f"\n--- FAIL/ERROR: {test} ---\n{tb}\n")
