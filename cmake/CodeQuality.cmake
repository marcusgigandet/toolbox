function(enforce_copyright)
    set(options "")
    set(oneValueArgs CONFIG_FILE SOURCE_DIR SCRIPT_DIR TARGET)
    set(multiValueArgs "")
    cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if(NOT ARG_SCRIPT_DIR)
        set(ARG_SCRIPT_DIR "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/../scripts/copyright")
    endif()

    add_custom_target(enforce_copyright
            COMMAND python3 "${ARG_SCRIPT_DIR}/copyright.py"
            --config "${ARG_CONFIG_FILE}"
            --directory "${ARG_SOURCE_DIR}"
            COMMENT "Syncing copyright headers with Git history"
            VERBATIM
    )
    add_dependencies(${ARG_TARGET} enforce_copyright)
endfunction()

function(enforce_clang_format)
    set(options "")
    set(oneValueArgs TARGET)
    set(multiValueArgs FILES)
    cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    find_program(CLANG_FORMAT_EXE clang-format REQUIRED)
    add_custom_target(enforce_clang_format
            COMMAND clang-format -i ${ARG_FILES}
            COMMENT "Running clang-format on files"
            VERBATIM
    )
    add_dependencies(${ARG_TARGET} enforce_clang_format)
endfunction()

function(generate_clangd_compdb)
    set(options "")
    set(oneValueArgs TARGET DEST_DIR)
    set(multiValueArgs "")
    cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    add_custom_command(TARGET ${ARG_TARGET} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${CMAKE_BINARY_DIR}/compile_commands.json
            ${ARG_DEST_DIR}/compile_commands.json
            COMMENT "Copying compile_commands.json to ${ARG_DEST_DIR}/compile_commands.json"
            VERBATIM
    )
endfunction()