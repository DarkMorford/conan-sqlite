from conans import ConanFile, VisualStudioBuildEnvironment, tools
import os


class SqliteConan(ConanFile):
    name = "sqlite"
    version = "3.19.3"
    version_string = "3190300"
    license = "MIT"
    url = "https://github.com/DarkMorford/conan-sqlite"
    description = "SQLite is a self-contained, high-reliability, embedded, full-featured, public-domain, SQL database engine."

    exports = "CMakeLists.txt", "sqlite3.def"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    @property
    def source_dir(self):
        return ("sqlite-amalgamation-%s" % self.version_string)

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.download("https://sqlite.org/2017/sqlite-amalgamation-3190300.zip", "sqlite.zip")
        tools.check_sha1("sqlite.zip", "e013f08dc8dc138d7b169d09433dbcea94721441")
        tools.unzip("sqlite.zip")
        os.remove("sqlite.zip")

    def build(self):
        os.chdir(self.source_dir)

        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cflags = []
            cflags.append("/DSQLITE_ENABLE_COLUMN_METADATA")
            cflags.append("/DSQLITE_ENABLE_RTREE")
            cflags.append("/DSQLITE_ENABLE_FTS5")
            cflags.append("/%s" % self.settings.compiler.runtime)

            ldflags = []

            build_env = VisualStudioBuildEnvironment(self)
            with tools.environment_append(build_env.vars):
                vcvars = tools.vcvars_command(self.settings)

                # Always build the command-line binary without debug info
                self.run("%s && cl %s sqlite3.c shell.c /Fe:sqlite3.exe" % (vcvars, " ".join(cflags)))

                if self.settings.build_type == "Debug":
                    cflags.append("/Zi")
                    cflags.append("/Fd:sqlite3.pdb")
                    if self.options.shared:
                        ldflags.append("/debug")

                if self.options.shared:
                    # Build shared library
                    self.run("%s && cl /c %s sqlite3.c" % (vcvars, " ".join(cflags)))
                    self.run("%s && link %s /dll /def:../sqlite3.def sqlite3.obj" % (vcvars, " ".join(ldflags)))
                else:
                    # Build static library
                    self.run("%s && cl /c %s sqlite3.c" % (vcvars, " ".join(cflags)))
                    self.run("%s && lib %s sqlite3.obj" % (vcvars, " ".join(ldflags)))
        else:
            raise Exception("Only MSVC compiler currently implemented.")

    def package(self):
        # Always copy headers
        self.copy("*.h", dst="include", src=self.source_dir)

        if self.settings.os == "Windows":
            self.copy("sqlite3.exe", dst="bin", src=self.source_dir)
            self.copy("sqlite3.pdb", dst="lib", src=self.source_dir)
            if self.options.shared:
                self.copy("sqlite3.lib", dst="lib", src=self.source_dir)
                self.copy("sqlite3.dll", dst="bin", src=self.source_dir)
            else:
                self.copy("sqlite3.lib", dst="lib", src=self.source_dir)

    def package_info(self):
        # Declare libraries that we generate
        self.cpp_info.libs = ["sqlite3"]

        # Add path to binary utilities
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
