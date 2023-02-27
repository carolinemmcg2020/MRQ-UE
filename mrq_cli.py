# Copyright Epic Games, Inc. All Rights Reserved

"""
This is a commandline script that can be used to execute local and remote renders from Unreal.
This script can be executed in Editor or via commandline.

This script has several modes:
    

    sequence:
        This mode allows you to specify a specific level sequence, map and movie render queue preset to render.
        Command:
            ` py mrq_cli.py sequence my_level_sequence_name my_map_name my_mrq_preset_name `

    

    --user: This options sets the author on the render job. If None is provided, the current logged-in user is used.


Editor CMD window:
    py mrq_cli.py <--remote> sequence sequence_name map mrq_preset_name

Editor Commandline:
    UnrealEditor.exe uproject_name/path <startup-args> -ExecCmds="py mrq_cli.py sequence sequence_name map mrq_preset_name --cmdline"

In a commandline interface, it is very important to append `--cmdline` to the script args as this will tell the editor
to shut down after a render is complete. Currently, this is the only method to keep the editor open till a render is
complete due to the default python commandlet assuming when a python script ends, the editor needs to shut down.
This behavior is not ideal as PIE is an asynchronous process we need to wait for during rendering.
"""

import argparse

from mrq_cli_modes import (
    render_sequence,
)

if __name__ == "__main__":

    # A parser to hold all arguments we want available on sub parsers.
    global_parser = argparse.ArgumentParser(
        description="This parser contains any global arguments we would want available on subparsers",
        add_help=False
    )
    # Determine if the editor was run from a commandline
    global_parser.add_argument(
        "--cmdline",
        action='store_true',
        help="Flag for noting execution from commandline. "
             "This will shut the editor down after a render is complete or failed."
    )

    # Create the main entry parser
    parser = argparse.ArgumentParser(
        prog="PYMoviePipelineCLI",
        description="Commandline Interface for rendering MRQ jobs"
    )

    # Create sub commands
    sub_commands = parser.add_subparsers(help="Sub-commands help")


    # Create a sub command used to render a specific sequence with a map and mrq preset
    sequence_parser = sub_commands.add_parser(
        "sequence",
        parents=[global_parser],
        help="Command to render a specific sequence, map, mrq preset and output directory."
    )

    # Add arguments for the sequence parser
    render_sequence.setup_sequence_parser(sequence_parser)


    # Process the args using the argument execution functions
    args = parser.parse_args()
    args.func(args)
