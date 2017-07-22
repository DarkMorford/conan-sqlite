from conans import ConanFile, CMake, tools
import os


class SqliteConan(ConanFile):
    name = "sqlite"
    version = "3.19.3"
    license = "<Put the package license here>"
    url = "<Package recipe repository url here, for issues about the package>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.download("https://sqlite.org/2017/sqlite-amalgamation-3190300.zip", "sqlite.zip")
        tools.check_sha1("sqlite.zip", "e013f08dc8dc138d7b169d09433dbcea94721441")
        tools.unzip("sqlite.zip")
        os.remove("sqlite.zip")

    def build(self):
        cmake = CMake(self)
        self.run('cmake hello %s' % cmake.command_line)
        self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="hello")
        self.copy("*hello.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hello"]
