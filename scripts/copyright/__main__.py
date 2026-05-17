"""
Copyright 2026 Marcus Gigandet

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import sys
from pathlib import Path

from .copyright import CopyrightEnforcer, CopyrightStatus, load_config


def main() -> int:
    """
    Entry-point for the copyright script.

    :return: Exit code.
    """
    parser = argparse.ArgumentParser(description="Copyright enforcement tool")

    parser.add_argument("--config", default="config.toml")
    parser.add_argument("--directory", default=".")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--override", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    config = load_config(Path(args.config))

    if not config:
        print(CopyrightStatus.NO_CONFIG.message)
        return CopyrightStatus.NO_CONFIG.number

    # Check for license
    if not config["copyright"]["license"]:
        print(CopyrightStatus.NO_LICENSE_GIVEN.message)
        return CopyrightStatus.NO_LICENSE_GIVEN.number

    enforcer = CopyrightEnforcer(
        config=config,
        root_dir=Path(args.directory),
        fix=args.fix if args.fix or args.override else config["copyright"]["fix"],
        verbose=args.verbose,
    )

    status = enforcer.run()

    if args.verbose:
        print(status)

    return status.number


if __name__ == "__main__":
    sys.exit(main())
