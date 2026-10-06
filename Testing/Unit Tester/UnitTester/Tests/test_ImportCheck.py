import os

from .baseUnitTest import BaseUnitTest, IDMG
from ..src.constants.Paths import SrcPath


class ImportCheckTest(BaseUnitTest):
    # =============== package =================================================

    # A folder named 'AGIDMGen' with no '__init__.py' (the repo's own top-level package folder) imports
    #   as an empty namespace package, so a wrong sys.path still "imports" -- check it is the source
    def test_package_importedFromSource(self):
        self.assertEqual(os.path.dirname(os.path.abspath(IDMG.__file__)), os.path.join(SrcPath, "AGIDMGen"))

    def test_all_everyNameExported(self):
        for name in IDMG.__all__:
            self.assertTrue(hasattr(IDMG, name), f"'{name}' is in __all__ but not exported")
