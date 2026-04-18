# Toolbox

## Scripts
### Copyright

#### Overview

Copyright is an enforcement tool for inserting copyright headers for each file in a project.

Configureable via `config.toml`:
- C / C++`
- Rust
- Python
- Ada
- etc.

#### Setup

Below is an example toml for configuring language support:
```toml
[tool]
fix = true
default_year = "2026"
author = "Marcus Gigandet"
license = "apache_2_0"

[licenses.apache_2_0]
file = "licenses/apache-2.0.txt"

[languages.cpp]
extensions = [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hh", ".hxx", ".cppm", "ixx"]
block_start = "/*"
line_prefix = " * "
block_end = " */"

[languages.rust]
extensions = [".rs"]
line_prefix = "//"

[languages.python]
extensions = [".py"]
block_start = '"""'
block_end = '"""'

[languages.ada]
extensions = [".adb", ".ads"]
line_prefix = "--"
```

#### Usage

Run the tool:

```bash
python3 copyright.py --config config.toml --directory . --verbose
```

**Note**: The tool recursively fixes all files from directory.

## cmake
### CodeQuality.cmake

Example usage:
```cmake
set(MODULES ...)
set(SOURCES ...)

include(<path-to-toolbox>/toolbox/cmake/CodeQuality.cmake)
enforce_clang_format(
        TARGET ${PROJECT_NAME}
        FILES ${MODULES} ${SOURCES}
)
enforce_copyright(
        TARGET ${PROJECT_NAME}
        CONFIG_FILE "${CMAKE_CURRENT_SOURCE_DIR}/config.toml"
        SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src"
)
generate_clangd_compdb(
        TARGET ${PROJECT_NAME}
        DEST_DIR "${CMAKE_CURRENT_SOURCE_DIR}"
)
```