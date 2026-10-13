##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple
import FixRaidenBoss2 as FRB
from FixRaidenBoss2 import AhoCorasickBuilder, AhoCorasickSingleton
##### EndExtImports


##### LocalImports
from .ModLoaders import ModLoaders
from .ModDownloadRepos import ModDownloadGameFolders
from ..data.ModDownloadData import ModDownloadData
from ..data.ModNameData import ModNameData, ModNamePartData
from ..exceptions.Error import Error
from ..model.ModName import ModName
##### EndLocalImports


##### Script
#: Anime Game Remap's ``FixRaidenBoss2.GameTypeId`` for each mod loader's game
ModNameGameTypeIds: Dict[ModLoaders, int] = {ModLoaders.GIMI: 0, ModLoaders.WWMI: 1}

# what is ignored in a name: case, spaces, '_' and '-' ('Hu Tao', 'hu_tao' and 'HuTao' are one name)
_IgnoredNameChars = re.compile(r"[\s_\-]+")


class ModNames():
    """
    The names of the characters an identity mod can be generated for, and the other names (aliases) each one
    can be asked for by, as Anime Game Remap names its mod types

    :raw-html:`<br />`

    A mod is named as Anime Game Remap names its mod type (eg. ``Raiden``, ``AyakaSpringBloom``), or in the same
    style when Anime Game Remap has no mod type for the character. A mod can be asked for by:

    * its name
    * the name of its download folder (eg. ``RaidenShogun``)
    * Anime Game Remap's aliases for its mod type (eg. ``Ei``), read from Anime Game Remap's ``FixRaidenBoss2.ModTypes``
    * this library's own aliases for it (see :attr:`ModNameData`)

    .. tip::
        The names and aliases are not case sensitive, and spaces, ``_`` and ``-`` in them are ignored (``hu tao`` is ``HuTao``)

    :raw-html:`<br />`

    .. note::
        As in Anime Game Remap, a name is found with the `Aho-Corasick <https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm>`_ algorithm: the longest name or alias found
        inside the text asked for is the one chosen (``RaidenShogunMod`` is ``Raiden``, and ``LumineHeaven`` is ``LumineHeaven`` rather than ``Lumine``)
    """

    _modNames: Dict[ModLoaders, Dict[str, ModName]] = {}
    _dfas: Dict[ModLoaders, AhoCorasickSingleton] = {}
    _dataKeys: Dict[ModLoaders, Tuple[Any, ...]] = {}

    @classmethod
    def normalize(cls, name: str) -> str:
        """
        Puts a name the way it is looked up: in lowercase, without spaces, ``_`` or ``-``

        Parameters
        ----------
        name: :class:`str`
            The name

        Returns
        -------
        :class:`str`
            The name as it is looked up
        """

        return _IgnoredNameChars.sub("", name).lower()

    @classmethod
    def clear(cls):
        """
        Forgets the names already looked up, so the next lookup reads :attr:`ModNameData`, :attr:`ModDownloadData`
        and Anime Game Remap's mod types again

        .. note::
            A change to :attr:`ModNameData` or :attr:`ModDownloadData` is noticed without this; a change to Anime Game
            Remap's mod types is not
        """

        cls._modNames.clear()
        cls._dfas.clear()
        cls._dataKeys.clear()

    @classmethod
    def getAGRemapAliases(cls, loader: ModLoaders) -> Dict[str, List[str]]:
        """
        Retrieves Anime Game Remap's aliases for its mod types of a game

        Parameters
        ----------
        loader: :class:`ModLoaders`
            The mod loader

        Returns
        -------
        Dict[:class:`str`, List[:class:`str`]]
            The aliases of each of Anime Game Remap's mod types, by the mod type's name
        """

        gameTypeId = ModNameGameTypeIds[loader]
        result = {}
        for modTypeEnum in FRB.ModTypes:
            modType = modTypeEnum.value
            if (int(modType.gameTypeId) == gameTypeId):
                result[modType.name] = list(modType.aliases)
        return result

    @classmethod
    def _build(cls, loader: ModLoaders):
        game = ModDownloadGameFolders[loader]
        names = {folder: (name, aliases) for name, (folder, aliases) in ModNameData.get(game, {}).items()}
        agRemapAliases = cls.getAGRemapAliases(loader)
        bases = ModNamePartData.get(game, {})

        modNames = {}
        for folder in ModDownloadData.get(game, {}):
            name, ownAliases = names.get(folder, (folder, []))

            aliases = []
            seen = {cls.normalize(name)}
            for alias in list(ownAliases) + agRemapAliases.get(name, []) + [folder]:
                key = cls.normalize(alias)
                if (key not in seen):
                    seen.add(key)
                    aliases.append(alias)

            modNames[name] = ModName(loader, name, folder, aliases, base = bases.get(name))

        # the mods' own names first, so an alias can never take a mod's name from it
        keywords = {}
        for modName in modNames.values():
            keywords[cls.normalize(modName.name)] = modName
        for modName in modNames.values():
            for alias in modName.aliases:
                keywords.setdefault(cls.normalize(alias), modName)

        dfa = AhoCorasickSingleton(AhoCorasickBuilder())
        dfa.setup(keywords)

        cls._modNames[loader] = dict(sorted(modNames.items(), key = lambda item: item[0].lower()))
        cls._dfas[loader] = dfa

    @classmethod
    def _getDataKey(cls, loader: ModLoaders) -> Tuple[Any, ...]:
        game = ModDownloadGameFolders[loader]
        names = ModNameData.get(game, {})
        return (tuple(ModDownloadData.get(game, {})), tuple((name, folder, tuple(aliases)) for name, (folder, aliases) in names.items()),
                tuple(ModNamePartData.get(game, {}).items()))

    @classmethod
    def _getDFA(cls, loader: ModLoaders) -> AhoCorasickSingleton:
        # rebuilt when the data it was built from changes (eg. a new download folder)
        dataKey = cls._getDataKey(loader)
        if (cls._dataKeys.get(loader) != dataKey):
            cls._build(loader)
            cls._dataKeys[loader] = dataKey
        return cls._dfas[loader]

    @classmethod
    def _getLoaders(cls, loaders: Optional[Iterable[ModLoaders]]) -> List[ModLoaders]:
        return list(ModLoaders) if (loaders is None) else [loader for loader in ModLoaders if (loader in set(loaders))]

    @classmethod
    def getAll(cls, loaders: Optional[Iterable[ModLoaders]] = None) -> List[ModName]:
        """
        Retrieves the names of every character with a download folder an identity mod can be generated from

        Parameters
        ----------
        loaders: Optional[Iterable[:class:`ModLoaders`]]
            The games, by their mod loaders, to list the characters of. If this value is ``None``, every game's :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        List[:class:`ModName`]
            The characters' names, in alphabetical order of :attr:`ModName.name`
        """

        result = []
        for loader in cls._getLoaders(loaders):
            cls._getDFA(loader)
            result += cls._modNames[loader].values()
        return sorted(result, key = lambda modName: (modName.name.lower(), modName.loader.value))

    @classmethod
    def _searchAll(cls, txt: str, loaders: Optional[Iterable[ModLoaders]]) -> List[ModName]:
        # the longest name or alias found, in any of the games; more than one result only when two games' are as long
        found = []
        normalized = cls.normalize(txt)
        for loader in cls._getLoaders(loaders):
            keyword, modName = cls._getDFA(loader).dfa.getMaximal(normalized, errorOnNotFound = False)
            if (modName is not None):
                found.append((len(keyword), modName))

        if (not found):
            return []
        longest = max(length for length, _ in found)
        return [modName for length, modName in found if (length == longest)]

    @classmethod
    def match(cls, txt: str, loaders: Optional[Iterable[ModLoaders]] = None) -> Optional[ModName]:
        """
        Finds the character whose name or alias a text IS, in any of the games: unlike :meth:`search`, a name found
        inside a longer text does not count (``ei`` is Raiden, but ``Heizo`` is no character, though ``Ei`` is in it)

        :raw-html:`<br />`

        The text is not case sensitive, and its spaces, ``_`` and ``-`` are ignored (see :meth:`normalize`)

        Parameters
        ----------
        txt: :class:`str`
            The text

        loaders: Optional[Iterable[:class:`ModLoaders`]]
            The games, by their mod loaders, to look in. If this value is ``None``, every game :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Optional[:class:`ModName`]
            The character's names, or ``None`` if the text is no character's name (or is one of each of two games)
        """

        normalized = cls.normalize(txt)
        found = []
        for loader in cls._getLoaders(loaders):
            modName = cls._getDFA(loader).dfa.getKeyVal(normalized, errorOnNotFound = False)
            if (modName is not None):
                found.append(modName)
        return found[0] if (len(found) == 1) else None

    @classmethod
    def getParts(cls, txt: str, loaders: Optional[Iterable[ModLoaders]] = None) -> List[ModName]:
        """
        Finds every part of the character whose base name a text IS (see :attr:`ModName.base`): eg. ``Carlotta`` is
        ``CarlottaBody``, ``CarlottaHairCrystal`` and ``CarlottaHairNormal``

        :raw-html:`<br />`

        The text may also be a name or alias of a whole character that has parts of its own (``Augusta`` is
        ``AugustaHelm``), and is matched as :meth:`match` matches: as a whole, in any case, ignoring spaces, ``_`` and ``-``.
        A skin's parts are not its character's: ``Carlotta`` is not ``CarlottaSummerBody``, whose base is ``CarlottaSummer``

        Parameters
        ----------
        txt: :class:`str`
            The text

        loaders: Optional[Iterable[:class:`ModLoaders`]]
            The games, by their mod loaders, to look in. If this value is ``None``, every game :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        List[:class:`ModName`]
            The parts, in alphabetical order, or none if the text is no character's base name
        """

        bases = {cls.normalize(txt)}
        whole = cls.match(txt, loaders)
        if (whole is not None):
            bases.add(cls.normalize(whole.name))
        return [modName for modName in cls.getAll(loaders) if (modName.base is not None and cls.normalize(modName.base) in bases)]

    @classmethod
    def search(cls, txt: str, loaders: Optional[Iterable[ModLoaders]] = None) -> Optional[ModName]:
        """
        Finds the character a text names, by its name or one of its aliases, in any of the games (see :class:`ModNames`)

        .. note::
            As in Anime Game Remap, a text that names characters of two games equally well (the longest name found in it is
            as long in both) is not guessed at: no character is found

        Parameters
        ----------
        txt: :class:`str`
            The text to search

        loaders: Optional[Iterable[:class:`ModLoaders`]]
            The games, by their mod loaders, to search. If this value is ``None``, every game :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Optional[:class:`ModName`]
            The character's names, or ``None`` if the text names no character (or one of each of two games)
        """

        found = cls._searchAll(txt, loaders)
        return found[0] if (len(found) == 1) else None

    @classmethod
    def find(cls, txt: str, loaders: Optional[Iterable[ModLoaders]] = None) -> ModName:
        """
        Finds the character a text names, by its name or one of its aliases, in any of the games (see :class:`ModNames`)

        Parameters
        ----------
        txt: :class:`str`
            The text to search

        loaders: Optional[Iterable[:class:`ModLoaders`]]
            The games, by their mod loaders, to search. If this value is ``None``, every game :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`Error`
            If the text names no character, or names characters of two games equally well

        Returns
        -------
        :class:`ModName`
            The character's names
        """

        found = cls._searchAll(txt, loaders)
        if (len(found) > 1):
            names = " and ".join(f"the {ModDownloadGameFolders[modName.loader]} character {modName.name}" for modName in found)
            raise Error(f"'{txt}' names both {names}: choose the game")
        if (not found):
            games = "/".join(ModDownloadGameFolders[loader] for loader in cls._getLoaders(loaders))
            raise Error(f"no {games} character called '{txt}' has a download folder")
        return found[0]
##### EndScript
