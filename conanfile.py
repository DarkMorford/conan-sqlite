from conans import ConanFile, CMake, tools
import os
import shutil


class SqliteConan(ConanFile):
    name = "sqlite"
    version = "3.19.3"
    version_string = "3190300"
    license = "MIT"
    url = "https://github.com/DarkMorford/conan-sqlite"
    description = "SQLite is a self-contained, high-reliability, embedded, full-featured, public-domain, SQL database engine."

    exports = "CMakeLists.txt", "sqlite3.def"
    generators = "cmake"

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
        # Move the CMakeLists file to the source directory
        shutil.move("CMakeLists.txt", os.path.join(self.source_dir, "CMakeLists.txt"))

        cmake_builder = CMake(self)
        self.run('cmake "%s" %s' % (self.source_dir, cmake_builder.command_line))
        self.run('cmake --build . %s' % cmake_builder.build_config)

    def package(self):
        # Always copy headers
        self.copy("*.h", dst="include", src=self.source_dir)

        if self.settings.os == "Windows":
            self.copy("sqlite3.pdb", dst="lib", src="lib")
            if self.options.shared:
                self.copy("*sqlite3.lib", dst="lib", src="lib")
                self.copy("*sqlite3.dll", dst="bin", src="bin")
            else:
                self.copy("*sqlite3.lib", dst="lib", src="lib")
        else:
            self.copy("*sqlite3.a", dst="lib", keep_path=False)
            self.copy("*sqlite3.so", dst="lib", keep_path=False)

    def package_info(self):
        # Declare libraries that we generate
        self.cpp_info.libs = ["sqlite3"]

        # Declare libraries that consumers need
        if not self.settings.os == "Windows":
            self.cpp_info.libs.append("dl", "pthread")

        # Add path to binary utilities
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
