from .baseUnitTest import BaseUnitTest, IDMG


class ErrorTest(BaseUnitTest):
    # =============== __init__ ===============================================

    def test_message_prefixedWithError(self):
        tests = [("bad mod", "ERROR: bad mod"),
                 ("", "ERROR: ")]

        for message, expected in tests:
            self.assertEqual(str(IDMG.Error(message)), expected)
