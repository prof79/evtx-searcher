#!/usr/bin/env python3
# -*- encoding: utf8 -*-
# main.py

#region Imports

import argparse
import traceback

from pathlib import Path
from rich import print

from app import EvtxSearcher

#endregion

#region Argument Parser

def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description='A Windows Event Log .evtx searcher.',
    )

    parser.add_argument(
        '--path',
        help='Path where .evtx files are located.',
    )

    return parser.parse_args()

#endregion

#region Main

def main() -> None:
    args = parse_args()

    path = args.path if args.path else Path.cwd()

    app = EvtxSearcher(path=path)

    app.run()

#endregion

#region Entry Point

if __name__ == '__main__':
    print()

    try:
        main()

    except KeyboardInterrupt:
        pass

    except Exception as ex:
        print(f'Unexpected error: {ex}')
        print()
        traceback.print_exc()

    print()
    print()

#endregion
