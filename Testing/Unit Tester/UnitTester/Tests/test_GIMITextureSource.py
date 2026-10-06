from .baseUnitTest import BaseUnitTest, IDMG


class GIMITextureSourceTest(BaseUnitTest):
    # =============== parse =================================================

    def test_parse_borrowerAndSource(self):
        tests = [("Bang=Body:A", "Bang", IDMG.GIMITextureSource("Body", "A")),
                 ("Eye=Body:A:plain", "Eye", IDMG.GIMITextureSource("Body", "A", IDMG.GIMITextureLayouts.Plain)),
                 ("Eye=Body:A:normalMap", "Eye", IDMG.GIMITextureSource("Body", "A", IDMG.GIMITextureLayouts.NormalMap))]
        for txt, borrower, source in tests:
            self.assertEqual(IDMG.GIMITextureSource.parse(txt), (borrower, source))

    def test_dict_roundTrip(self):
        for source in (IDMG.GIMITextureSource("Body", "A"), IDMG.GIMITextureSource("", "Head", IDMG.GIMITextureLayouts.Plain), IDMG.GIMITextureSource("Body", "B", IDMG.GIMITextureLayouts.NormalMap)):
            self.assertEqual(IDMG.GIMITextureSource.fromDict(source.toDict()), source)
        self.assertEqual(IDMG.GIMITextureSource("", "Head", IDMG.GIMITextureLayouts.Plain).toDict(), {"component": "", "object": "Head", "layout": "plain"})

    def test_badText_raises(self):
        for txt in ("Bang", "Bang=Body", "Bang=Body:A:shiny", "Bang=Body:A:plain:x"):
            with self.assertRaises(IDMG.Error, msg = txt):
                IDMG.GIMITextureSource.parse(txt)
