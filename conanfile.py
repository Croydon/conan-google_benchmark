from conans import ConanFile, CMake, tools
import shutil


class GoogleBenchmarkConan(ConanFile):
    name = "google_benchmark"
    version = "1.4.1"
    description = "A microbenchmark support library."
    url = "http://github.com/croydon/conan-google_benchmark"
    homepage = "https://github.com/google/benchmark"
    license = "Apache-2.0"
    settings = "arch", "build_type", "compiler", "os"
    options = {
        "enable_lto": [True, False],
        "enable_exceptions": [True, False],
        "shared": [True, False]
    }
    default_options = "enable_lto=False", "enable_exceptions=True", "shared=False"
    exports_sources = "CMakeLists.txt", "benchmarkConfig.cmake"
    generators = "cmake"

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def source(self):
        archive_url = "https://github.com/google/benchmark/archive/v{!s}.zip".format(self.version)
        tools.get(archive_url, sha256="61ae07eb5d4a0b02753419eb17a82b7d322786bb36ab62bd3df331a4d47c00a7")
        shutil.move("benchmark-{!s}".format(self.version), "benchmark")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["BENCHMARK_ENABLE_TESTING"] = "OFF"
        cmake.definitions["BENCHMARK_ENABLE_LTO"] = "ON" if self.options.enable_lto else "OFF"
        cmake.definitions["BENCHMARK_ENABLE_EXCEPTIONS"] = "ON" if self.options.enable_exceptions else "OFF"

        # See https://github.com/google/benchmark/pull/523
        if self.settings.os != "Windows":
            cmake.definitions["BENCHMARK_BUILD_32_BITS"] = "ON" if "64" not in str(self.settings.arch) else "OFF"
            cmake.definitions["BENCHMARK_USE_LIBCXX"] = "ON" if (str(self.settings.compiler.libcxx) == "libc++") else "OFF"
        else:
            cmake.definitions["BENCHMARK_USE_LIBCXX"] = "OFF"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="*.h", dst="include", src="include/benchmark", keep_path=False)
        self.copy("benchmarkConfig.cmake", dst=".", src=".", keep_path=False)
        self.copy(pattern="*", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = "benchmark"
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "rt"])
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("shlwapi")
