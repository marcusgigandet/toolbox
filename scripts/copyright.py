import argparse
import datetime
import re
import subprocess
import sys
from enum import Enum
from pathlib import Path


class CopyrightStatus(Enum):
    SUCCESS = (0, "OK", "No issues found")
    MISSING_HEADER = (1, "E001", "No license header found")
    INVALID_FORMAT = (2, "E002", "Header exists but format is invalid")
    INCORRECT_AUTHOR = (3, "E003", "Author name does not match expected")
    INCORRECT_YEAR = (4, "E004", "Year or year range is incorrect")
    MULTIPLE_HEADERS = (5, "E005", "More than one header found")
    UNEXPECTED_CONTENT = (6, "E006", "Header contains unexpected content")

    def __init__(self, number: int, short_code: str, message: str):
        self.number = number
        self.short_code = short_code
        self.message = message

    def __str__(self):
        return f"{self.short_code}: {self.message}"


def has_header_at_top(text: str) -> bool:
    """
    Checks whether the file starts with a valid license header.

    Looks for a C-style comment block (`/* ... */`) at the top that contains
    'Copyright'. Leading blank lines are ignored during the check.

    :param text: Full contents of the file.
    :return: True if a license header is detected at the top, False otherwise.
    """

    header_docstring = text.lstrip().split("*/", 1)[0]
    return header_docstring.startswith("/*") and "Copyright" in header_docstring


class CopyrightEnforcer:
    HEADER_TEMPLATE = """/*
 * Copyright {years} {author}
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""

    YEAR_REGEX = re.compile(r"(Copyright|@date) ([0-9]{4})(-[0-9]{4})?")

    def __init__(
        self,
        root_dir: Path,
        author: str,
        default_year: str,
        extensions: tuple[str, ...],
        fix: bool,
        verbose: bool,
    ):
        self.src_dir = root_dir
        self.author = author
        self.default_year = default_year
        self.extensions = extensions
        self.fix = fix
        self.verbose = verbose
        self.violations: list[Path] = []

    def git_years(self, file: Path) -> tuple[str, str]:
        """
        Returns a year range of the git history for the file.

        :param self:
        :param file: File being analyzed.
        :type file: Path
        :return: Year range for the file's git history.
        :rtype: tuple[str, str]
        """
        try:
            start = subprocess.run(
                [
                    "git",
                    "log",
                    "--follow",
                    "--format=%cd",
                    "--date=format:%Y",
                    str(file),
                ],
                stderr=subprocess.DEVNULL,
                capture_output=True,
                text=True,
            ).stdout.splitlines()[-1]
        except Exception:
            start = self.default_year

        try:
            end = subprocess.run(
                ["git", "log", "-1", "--format=%cd", "--date=format:%Y", str(file)],
                stderr=subprocess.DEVNULL,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except Exception:
            end = self.default_year

        return start or self.default_year, end or self.default_year

    def expected_years(self, file: Path) -> str:
        """
        Returns the expected copyright year string for a file.

        The year (or year range) is derived from the file's git history.
        If the first and last are the same, a single year is returned.
        Otherwise, a range in the form of "YYYY-YYYY" is returned.

        :param self:
        :param file: The file being examined.
        :type file: Path
        :return: Copyright year or year range.
        :rtype: str
        """
        start, end = self.git_years(file)
        return start if start == end else f"{start}-{end}"

    def check_file(self, file: Path) -> bool:
        """
        Checks if the file has a copyright header.

        :param self:
        :param file: The file being checked.
        :type file: Path
        :return: True if it has a copyright header, otherwise False.
        :rtype: bool
        """
        text = file.read_text(encoding="utf-8", errors="ignore")

        if not has_header_at_top(text):
            return False

        expected = self.expected_years(file)
        return (
            bool(self.YEAR_REGEX.search(text.replace("\n", " "))) and expected in text
        )

    def fix_file(self, file: Path) -> None:
        """
        Updates the file to have a copyright header at the top of the file.

        :param self:
        :param file: File being fixed.
        :type file: Path
        """
        expected_years = self.expected_years(file)
        text = file.read_text(encoding="utf-8", errors="ignore")

        if "Copyright" in text:
            text = self.YEAR_REGEX.sub(
                rf"\1 {expected_years}",
                text,
            )
        else:
            header = self.HEADER_TEMPLATE.format(
                years=expected_years,
                author=self.author,
            )
            text = header + text

        file.write_text(text, encoding="utf-8")

    def process_file(self, file: Path) -> None:
        """
        Checks file for a valid copyright header and if fixing is enabled,
        inserts a copyright header.

        :param self:
        :param file: File being processed.
        :type file: Path
        """
        if not self.check_file(file):
            self.violations.append(file)
            if self.fix:
                self.fix_file(file)

    def run(self) -> CopyrightStatus:
        """
        Processes all files.

        :param self:
        :return: Status code of the program.
        :rtype: CopyrightStatus
        """
        for file in self.src_dir.rglob("*"):
            if file.suffix in self.extensions:
                self.process_file(file)

        if self.violations:
            for i, file in enumerate(self.violations):
                print(
                    f"[{i + 1}/{len(self.violations)}] Inserting copyright stub for {file}"
                )

            if not self.fix:
                return CopyrightStatus.MISSING_HEADER

        return CopyrightStatus.SUCCESS


def main() -> int:
    """
    Entry-point for the copyright script.

    Processes arguments passed via the commandline.

    :return: Returns 0 on success
    :rtype: int
    """
    parser = argparse.ArgumentParser(description="Copyright enforcement tool")
    parser.add_argument(
        "--directory",
        default="./",
        help="Directory being checked relative to calling directory",
    )
    parser.add_argument(
        "--author",
        default="",
    )
    parser.add_argument(
        "--default-year",
        default=f"{datetime.datetime.now().year}",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix violations",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Display all log messages",
    )
    args = parser.parse_args()

    # Todo: Add support for custom extensions and additional languages
    enforcer = CopyrightEnforcer(
        root_dir=Path(args.directory),
        author=args.author,
        default_year=args.default_year,
        extensions=(".c", ".cpp", ".cppm", ".cxx", ".cc", ".c++", ".hpp", ".h", ".h++"),
        fix=args.fix,
        verbose=args.verbose,
    )

    copyright_return_status = enforcer.run()
    if args.verbose:
        print(copyright_return_status)
    return copyright_return_status.number


if __name__ == "__main__":
    sys.exit(main())
