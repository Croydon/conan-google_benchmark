from conans import ConanFile, CMake, tools
import os


class GoogleBenchmarkConan(ConanFile):
    name = "benchmark"
    version = "1.4.1"
    description = "A microbenchmark support library."
    url = "https://github.com/croydon/conan-google_benchmark"
    homepage = "https://github.com/google/benchmark"
    license = "Apache-2.0"
    settings = "arch", "build_type", "compiler", "os"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_exceptions": [True, False],
        "enable_lto": [True, False],
        "enable_testing": [True, False],
        "enable_gtest_tests": [True, False]
    }
    default_options = "shared=False", "fPIC=True", "enable_exceptions=True", "enable_lto=False", "enable_testing=False","enable_gtest_tests=False"
    exports = ["LICENSE"]
    exports_sources = ["CMakeLists.txt", "benchmarkConfig.cmake"]
    generators = "cmake"

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def source(self):
        archive_url = "https://github.com/google/benchmark/archive/v{!s}.zip".format(self.version)
        tools.get(archive_url, sha256="61ae07eb5d4a0b02753419eb17a82b7d322786bb36ab62bd3df331a4d47c00a7")
        os.rename("benchmark-{!s}".format(self.version), self.source_subfolder)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.shared  # See https://github.com/google/benchmark/issues/639 - no Windows shared support for now
        if self.options.enable_testing == False:
            self.options.enable_gtest_tests = False

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.settings.os != 'Windows' and self.options.shared else "OFF"
        cmake.definitions['BENCHMARK_ENABLE_TESTING'] = "ON" if self.options.enable_testing else "OFF"
        cmake.definitions['BENCHMARK_ENABLE_GTEST_TESTS'] = "ON" if self.options.enable_gtest_tests and self.options.enable_testing else "OFF"
        cmake.definitions["BENCHMARK_ENABLE_LTO"] = "ON" if self.options.enable_lto else "OFF"
        cmake.definitions["BENCHMARK_ENABLE_EXCEPTIONS"] = "ON" if self.options.enable_exceptions else "OFF"

        # See https://github.com/google/benchmark/pull/638 for Windows 32 build explanation
        if self.settings.os != "Windows":
            cmake.definitions["BENCHMARK_BUILD_32_BITS"] = "ON" if "64" not in str(self.settings.arch) else "OFF"
            cmake.definitions["BENCHMARK_USE_LIBCXX"] = "ON" if (str(self.settings.compiler.libcxx) == "libc++") else "OFF"
        else:
            cmake.definitions["BENCHMARK_USE_LIBCXX"] = "OFF"

        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build_requirements(self):
        if self.options.enable_gtest_tests:
            self.build_requires("gtest/1.8.0@bincrafters/stable")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        self.copy("benchmarkConfig.cmake", dst=".", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.libs.append("shlwapi")
