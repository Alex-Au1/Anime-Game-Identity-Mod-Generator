import os
import tempfile
from unittest import mock

from .baseUnitTest import BaseUnitTest, IDMG


Data = {"GI": {"Raiden": {"4_0": ("RaidenShogun", {"RaidenShogunHash.json": "AGIDMGen", "RaidenShogunHead.ib": "AGRemap"}),
                          "6_8": ("RaidenShogun", {"RaidenShogunHash.json": "AGIDMGen", "RaidenShogunHead.ib": "AGIDMGen"})},
               "Yelan": {"4_0": ("Yelan", {"YelanHash.json": "AGIDMGen"})}},
        "WuWa": {"SanhuaExorcist": {"2_5": ("SanhuaExorcist", {"SanhuaExorcistMetadata.json": "AGRemap"})}}}
Aliases = {"GI": {"RaidenEi": "Raiden", "YaoYao": "Yaoyao"}, "WuWa": {"SanhuaSkin1": "SanhuaExorcist"}}


class ModDownloaderTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        for target, values in ((IDMG.ModDownloadData, Data), (IDMG.ModDownloadAliases, Aliases)):
            patcher = mock.patch.dict(target, values, clear = True)
            patcher.start()
            self.addCleanup(patcher.stop)

        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)

    def makeLocal(self, repo: str, path: str, content: bytes) -> str:
        root = os.path.join(self._temp.name, repo)
        full = os.path.join(root, *path.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok = True)
        with open(full, "wb") as f:
            f.write(content)
        return root

    # =============== getName / getCharacters ===============================

    def test_getName_exactAliasOrAnyCase(self):
        tests = [(IDMG.ModLoaders.GIMI, "Raiden", "Raiden"), (IDMG.ModLoaders.GIMI, "raideNei", "Raiden"), (IDMG.ModLoaders.GIMI, "YELAN", "Yelan"),
                 (IDMG.ModLoaders.WWMI, "SanhuaSkin1", "SanhuaExorcist")]
        for loader, name, expected in tests:
            self.assertEqual(IDMG.ModDownloader.getName(loader, name), expected, name)

    def test_unknownName_raises(self):
        # Yaoyao is an alias' target with no listed folder
        for loader, name in ((IDMG.ModLoaders.WWMI, "Yelan"), (IDMG.ModLoaders.GIMI, "YaoYao"), (IDMG.ModLoaders.GIMI, "Yaoyao")):
            with self.assertRaises(IDMG.Error, msg = name):
                IDMG.ModDownloader.find(loader, name)

    def test_getCharacters_perGame(self):
        self.assertEqual(IDMG.ModDownloader.getCharacters(IDMG.ModLoaders.GIMI), ["Raiden", "Yelan"])
        self.assertEqual(IDMG.ModDownloader.getVersions(IDMG.ModLoaders.GIMI, "raiden"), ["4_0", "6_8"])

    # =============== find ==================================================

    def test_find_newestUnlessAsked(self):
        tests = [(None, "6_8", IDMG.ModDownloadRepos.AGIDMGen), ("5.0", "4_0", IDMG.ModDownloadRepos.AGRemap), ("3.0", "4_0", IDMG.ModDownloadRepos.AGRemap)]
        for version, expected, repo in tests:
            download = IDMG.ModDownloader.find(IDMG.ModLoaders.GIMI, "Raiden", version)
            self.assertEqual((download.name, download.version, download.prefix), ("Raiden", expected, "RaidenShogun"))
            self.assertEqual(download.files["RaidenShogunHead.ib"], repo)

    def test_getUrl_fromTheFilesRepo(self):
        download = IDMG.ModDownloader.find(IDMG.ModLoaders.GIMI, "Raiden", "4.0")
        self.assertEqual(IDMG.ModDownloader.getUrl(download, "RaidenShogunHead.ib"),
                         "https://github.com/nhok0169/Anime-Game-Remap/raw/master/Data/Mod%20Downloads/GI/Raiden/4_0/RaidenShogunHead.ib")
        self.assertEqual(IDMG.ModDownloader.getUrl(download, "RaidenShogunHash.json"),
                         "https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/raw/main/Data/Mod%20Downloads/GI/Raiden/4_0/RaidenShogunHash.json")

    # =============== download ==============================================

    def test_localFolders_copiedNotDownloaded(self):
        agRemap = self.makeLocal("ag", "GI/Raiden/4_0/RaidenShogunHead.ib", b"ib")
        own = self.makeLocal("own", "GI/Raiden/4_0/RaidenShogunHash.json", b"[]")
        downloader = IDMG.ModDownloader(localFolders = {IDMG.ModDownloadRepos.AGRemap: agRemap, IDMG.ModDownloadRepos.AGIDMGen: own})
        self.patchObj(IDMG.ModDownloader, "_downloadFile")

        out = os.path.join(self._temp.name, "out")
        download = downloader.download(IDMG.ModDownloader.find(IDMG.ModLoaders.GIMI, "Raiden", "4.0"), out)
        self.assertEqual(download.folder, out)
        self.assertEqual(sorted(os.listdir(out)), ["RaidenShogunHash.json", "RaidenShogunHead.ib"])
        IDMG.ModDownloader._downloadFile.assert_not_called()

    def test_fileMissingLocally_downloadedFromItsRepo(self):
        own = self.makeLocal("own", "GI/Raiden/4_0/RaidenShogunHash.json", b"[]")
        downloader = IDMG.ModDownloader(localFolders = {IDMG.ModDownloadRepos.AGIDMGen: own})
        self.patchObj(IDMG.ModDownloader, "_downloadFile", side_effect = lambda url, fileName, folder: open(os.path.join(folder, fileName), "wb").close())

        downloader.download(IDMG.ModDownloader.find(IDMG.ModLoaders.GIMI, "Raiden", "4.0"), os.path.join(self._temp.name, "out"))
        IDMG.ModDownloader._downloadFile.assert_called_once_with(
            "https://github.com/nhok0169/Anime-Game-Remap/raw/master/Data/Mod%20Downloads/GI/Raiden/4_0/RaidenShogunHead.ib",
            "RaidenShogunHead.ib", os.path.join(self._temp.name, "out"))

    def test_lfsPointer_refusedFromALocalFolderOrADownload(self):
        pointer = b"version https://git-lfs.github.com/spec/v1\noid sha256:11c8\nsize 51744\n"
        own = self.makeLocal("own", "GI/Raiden/4_0/RaidenShogunHash.json", b"[]")
        agRemap = self.makeLocal("ag", "GI/Raiden/4_0/RaidenShogunHead.ib", pointer)
        downloader = IDMG.ModDownloader(localFolders = {IDMG.ModDownloadRepos.AGRemap: agRemap, IDMG.ModDownloadRepos.AGIDMGen: own})
        with self.assertRaises(IDMG.DownloadFailed) as context:
            downloader.download(IDMG.ModDownloader.find(IDMG.ModLoaders.GIMI, "Raiden", "4.0"), os.path.join(self._temp.name, "out"))
        self.assertIn("LFS pointer", str(context.exception))

        def serveThePointer(url, fileName, folder):
            with open(os.path.join(folder, fileName), "wb") as f:
                f.write(pointer if fileName.endswith(".ib") else b"[]")
        self.patchObj(IDMG.ModDownloader, "_downloadFile", side_effect = serveThePointer)
        with self.assertRaises(IDMG.DownloadFailed):
            IDMG.ModDownloader().download(IDMG.ModDownloader.find(IDMG.ModLoaders.GIMI, "Raiden", "4.0"), os.path.join(self._temp.name, "out2"))

    def test_nothingArrived_raises(self):
        own = self.makeLocal("own", "GI/Raiden/4_0/RaidenShogunHash.json", b"[]")
        self.patchObj(IDMG.ModDownloader, "_downloadFile")
        with self.assertRaises(IDMG.DownloadFailed) as context:
            IDMG.ModDownloader(localFolders = {IDMG.ModDownloadRepos.AGIDMGen: own}).download(IDMG.ModDownloader.find(IDMG.ModLoaders.GIMI, "Raiden", "4.0"), os.path.join(self._temp.name, "out"))
        self.assertIn("did not arrive", str(context.exception))

    def test_isLfsPointer_onlyTheSmallHeaderFile(self):
        tests = [(b"version https://git-lfs.github.com/spec/v1\noid sha256:ab\nsize 3\n", True), (b"[]", False),
                 (b"version https://git-lfs.github.com/spec/v1" + bytes(2000), False), (b"", False)]
        for i, (content, expected) in enumerate(tests):
            path = self.makeLocal("p", f"f{i}", content)
            self.assertEqual(IDMG.ModDownloader.isLfsPointer(os.path.join(path, f"f{i}")), expected, i)

    def test_failedDownload_raisesDownloadFailed(self):
        downloader = IDMG.ModDownloader()
        import FixRaidenBoss2
        with mock.patch.object(FixRaidenBoss2, "FileDownload", side_effect = RuntimeError("request failed: 404")):
            with self.assertRaises(IDMG.DownloadFailed) as context:
                downloader.download(IDMG.ModDownloader.find(IDMG.ModLoaders.GIMI, "Yelan"), os.path.join(self._temp.name, "out"))
        self.assertIn("404", str(context.exception))
