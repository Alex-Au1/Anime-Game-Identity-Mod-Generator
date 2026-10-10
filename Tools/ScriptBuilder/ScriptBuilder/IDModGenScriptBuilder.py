import ast
from collections import defaultdict
from typing import Dict, List, Set
from types import ModuleType

from .AGRemapUtils import ScriptBuilder, PyFile, FromImport, PyPathTools


# IDModGenScriptBuilder: Compiles AGIDMGen's source into a single script, with AGRemapUtils' ScriptBuilder
#
# Differences from AG Remap's use of it:
#   - every module the package's '__init__.py' exports goes into the script, not only the ones the main
#       module reaches, so the script build's '__init__.py' can re-export the whole library
#   - the library's source files are only read, never written: AGRemapUtils' builder rewrites a module whose
#       credits differ from AG Remap's, and AGIDMGen's credits are its own
#   - the main function is 'main', and '__main__.py' keeps its own imports
#   - two modules defining the same top-level name would silently overwrite each other once flattened into
#       one file, so that is refused before anything is written
class IDModGenScriptBuilder(ScriptBuilder):
    def __init__(self, scriptFolder: str, scriptBasePath: str, modules: Dict[str, ModuleType], rootModule: str,
                 moduleFolder: str, creditsLines: List[str], mainFunc: str, **kwargs):
        super().__init__(scriptFolder, scriptBasePath, modules, rootModule, moduleFolder, **kwargs)
        self._creditsLines = creditsLines
        self._mainFunc = mainFunc


    # readFile(filePath, module): Reads a source file, with AGIDMGen's credits as the expected ones
    def readFile(self, filePath: str, module: str) -> PyFile:
        result = PyFile(filePath, module, creditsLines = self._creditsLines)
        result.read()
        return result


    # getExportedModules(): Retrieves every module the package's '__init__.py' imports from, in its order
    #
    # note: ordered, never a plain set: the order modules are visited in is the order they are written in, and
    #   a set's order changes from one run to the next
    def getExportedModules(self) -> List[str]:
        initFile = self.readFile(self._moduleInitPath, f"{self._module}.__init__")
        return list(initFile.getLocalCalledModules())


    def _getNeighbourModules(self, module: str) -> List[str]:
        file = self.readFile(self.getModuleFilePath(module), module)
        self.addModuleFile(module, file)

        self._extImport += file.extImport
        self._extFromImports += file.extFromImports

        result = list(file.getLocalCalledModules())
        if (module == self._rootModule):
            result += [exported for exported in self.getExportedModules() if exported not in result]
        return result


    # getDefinedNames(module): Retrieves the top-level names a module's script sections define
    def getDefinedNames(self, module: str) -> Set[str]:
        result = set()
        for node in ast.parse(self._moduleFiles[module].getScriptStr()).body:
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))):
                result.add(node.name)
            elif (isinstance(node, (ast.Assign, ast.AnnAssign))):
                targets = node.targets if (isinstance(node, ast.Assign)) else [node.target]
                for target in targets:
                    result.update(name.id for name in ast.walk(target) if isinstance(name, ast.Name))
        return result


    # checkModules(): Refuses to compile a script that misses a module, or whose modules' top-level names
    #   would overwrite each other's
    #
    # note: AGRemapUtils' topological sort prints an error it hits and carries on, which leaves the modules
    #   after it out of the script; a module missing here is how that shows
    @ScriptBuilder.readModules
    def checkModules(self):
        missing = sorted(module for module, mod in self._modules.items()
                         if not self._moduleTopoOrder[module].visisted and not mod.__file__.endswith(("__init__.py", "__main__.py")))
        if (missing):
            raise ValueError("These modules did not make it into the script:\n  " + "\n  ".join(missing))

        definers = defaultdict(list)
        for module, dfsData in self._moduleTopoOrder.items():
            if (dfsData.visisted):
                for name in self.getDefinedNames(module):
                    definers[name].append(module)

        clashes = [f"{name}: {', '.join(modules)}" for name, modules in sorted(definers.items()) if len(modules) > 1]
        if (clashes):
            raise ValueError("These top-level names are defined by more than one module, and would overwrite each other in the script:\n  " + "\n  ".join(clashes))


    def getScriptStr(self) -> str:
        self.checkModules()
        return super().getScriptStr()


    # getScriptMainStr(): Retrieves the script build's '__main__.py'
    def getScriptMainStr(self) -> str:
        file = self.readFile(PyPathTools.getMainPath(self._moduleFolder), self._module)
        fromImport = FromImport(self._scriptModule, objects = [self._mainFunc])
        return f"{file.getExtImportStr()}\n{fromImport.toStr()}\n\n{file.getScriptStr()}\n"


    # getScriptInitStr(): Retrieves the script build's '__init__.py', re-exporting everything the package does
    def getScriptInitStr(self) -> str:
        file = self.readFile(self._moduleInitPath, self._module)
        objects = list(file.getLocalObjects())
        fromImport = FromImport(self._scriptModule, objects = objects)
        allTxt = ", ".join(f'"{ob}"' for ob in objects)
        return f"{fromImport.toStr()}\n\n__all__ = [{allTxt}]\n"


    # getFiles(): Retrieves every file of the script build, by its path
    def getFiles(self) -> Dict[str, str]:
        return {self._scriptPath: self.getScriptStr(), self._scriptMainPath: self.getScriptMainStr(), self._scriptInitPath: self.getScriptInitStr()}


    # build(): Writes the script build
    #
    # note: unlike AGRemapUtils' builder, this never writes the library's source files back (see the class's note)
    def build(self):
        for path, txt in self.getFiles().items():
            print(f"Creating {path}")
            with open(path, "w", encoding = "utf-8", newline = "\n") as f:
                f.write(txt)
