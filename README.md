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

#### Usage

Run the tool:

```bash
python3 -m scripts.copyright --config config.toml --directory . --verbose
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