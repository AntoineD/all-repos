from __future__ import annotations

import argparse
import functools
import os
from typing import Sequence
from typing import Generator

from all_repos import autofix_lib
from all_repos.config import Config
from all_repos.sed import _quote_cmd


def find_repos(
    config: Config,
) -> Generator[str, None, None]:
    for repo in config.get_cloned_repos():
        yield os.path.join(config.output_dir, repo)


def apply_fix(
    *,
    cmd: Sequence[str],
) -> None:
    autofix_lib.run(*cmd)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            'Similar to a distributed execution of a command in all the repos.'
        ),
        usage='%(prog)s [options] COMMAND',
    )
    autofix_lib.add_fixer_args(parser)
    parser.add_argument(
        '--branch-name', default='all-repos-exec',
        help='override the autofixer branch name (default `%(default)s`).',
    )
    parser.add_argument(
        '--commit-msg',
        help=(
            'override the autofixer commit message.  (default '
            'the command to execute.'
        ),
    )
    parser.add_argument(
        'command', help='the command to execute.',
    )

    args = parser.parse_args(argv)

    cmd = args.command.split()
    msg = args.commit_msg or f'{_quote_cmd(cmd)}'

    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=msg, branch_name=args.branch_name,
    )

    autofix_lib.fix(
        repos,
        apply_fix=functools.partial(apply_fix, cmd=cmd),
        config=config,
        commit=commit,
        autofix_settings=autofix_settings,
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
