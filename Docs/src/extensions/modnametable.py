#
# ===== modnametable =====
#
# The '.. modnametable::' directive: the table of every character's mod name, game, aliases and download folder,
# laid out as Anime Game Remap's mod type table in its commandOpts.rst. It is GENERATED at build time from the
# library's own AGIDMGen.ModNames (the hand-kept ModNameData, Anime Game Remap's aliases read live from
# FixRaidenBoss2, and each download folder's name), so the table can never drift from what the library accepts.
#
# Options:
#   :game: GI or WuWa, to list one game only (default: both)
#

import os
from typing import List

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

import AGIDMGen as IDMG


# how many aliases are put on one line of a cell
AliasesPerLine = 2


def aliasLines(aliases: List[str]) -> List[str]:
    """The aliases as the lines of a line block, a few per line, as Anime Game Remap's table writes them"""
    if (not aliases):
        return ["\\-"]

    groups = [aliases[i:i + AliasesPerLine] for i in range(0, len(aliases), AliasesPerLine)]
    return [f"| {', '.join(group)}{',' if (i < len(groups) - 1) else ''}" for i, group in enumerate(groups)]


class ModNameTable(SphinxDirective):
    has_content = False
    option_spec = {"game": directives.unchanged}

    def run(self) -> List[nodes.Node]:
        # the page is read again when the names or the download folders change, not only when its .rst does
        dataFolder = os.path.dirname(os.path.abspath(IDMG.data.ModNameData.__file__))
        for fileName in ("ModNameData.py", "ModDownloadData.py"):
            self.env.note_dependency(os.path.join(dataFolder, fileName))

        games = {IDMG.ModDownloadGameFolders[loader]: loader for loader in IDMG.ModLoaders}
        wanted = self.options.get("game")
        if (wanted is not None and wanted not in games):
            raise self.error(f"modnametable's :game: is one of {', '.join(games)}, not {wanted!r}")

        rows = []
        for game, loader in games.items():
            if (wanted is None or wanted == game):
                rows += [(modName, game) for modName in IDMG.ModNames.getAll([loader])]
        rows.sort(key = lambda row: (row[0].name.lower(), row[1]))

        lines = [".. list-table::", "   :widths: 22 10 46 22", "   :header-rows: 1", "   :class: mod-name-table", "",
                 "   * - Name", "     - Game", "     - Aliases", "     - Download Folder"]
        for modName, game in rows:
            aliases = [alias for alias in modName.aliases if (alias != modName.folder)]
            cell = aliasLines(aliases)
            lines.append(f"   * - **{modName.name}**")
            lines.append(f"     - {game}")
            lines.append(f"     - {cell[0]}")
            lines += [f"       {line}" for line in cell[1:]]
            lines.append(f"     - ``{modName.folder}``")

        container = nodes.container()
        self.state.nested_parse(StringList(lines, source = "modnametable"), self.content_offset, container)
        return container.children


def setup(app: Sphinx):
    app.add_directive("modnametable", ModNameTable)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
