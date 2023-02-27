# Copyright Epic Games, Inc. All Rights Reserved

"""
This script handles processing jobs for a specific sequence
"""

from webbrowser import get
import unreal

from getpass import getuser

from .utils import (
    render_queue,
    execute_render,
    project_settings,
    get_asset_data,

)


def setup_sequence_parser(subparser):
    """
    This method adds a custom execution function and args to a sequence subparser
    :param subparser: Subparser for processing custom sequences
    """
    # We will use the level sequence and the map as our context for
    # other subsequence arguments.
    subparser.add_argument(
        "sequence",
        type=str,
        help="The level sequence that will be rendered."
    )
    subparser.add_argument(
        "map",
        type=str,
        help="The map the level sequence will be loaded with for rendering."
    )

    # Get some information for the render queue
    subparser.add_argument(
        "mrq_preset",
        type=str,
        help="The MRQ preset used to render the current job."
    )
    # Get info for output dir
    subparser.add_argument(
        "render_out_dir",
        type=str,
        help="The output folder you want to render to."
    )

    # Function to process arguments
    subparser.set_defaults(func=_process_args)


def _process_args(args):
    """
    Function to process the arguments for the sequence subcommand
    :param args: Parsed Arguments from parser
    """

    # The queue subsystem behaves like a singleton so
    # clear all the jobs in the current queue.
    render_queue.delete_all_jobs()

    render_job = render_queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
    

    # Set the author on the job
    render_job.author = getuser()

    sequence_data_asset = get_asset_data(args.sequence, "Script/LevelSequence.LevelSequence")

    # Create a job in the queue
    unreal.log(f"Creating render job for `{sequence_data_asset.asset_name}`")
    render_job.job_name = sequence_data_asset.asset_name

    unreal.log(f"Setting the job sequence to `{sequence_data_asset.asset_name}`")
    render_job.sequence = sequence_data_asset.to_soft_object_path()

    map_data_asset = get_asset_data(args.map, "Script/Engine.World")
    unreal.log(f"Setting the job map to `{map_data_asset.asset_name}`")
    render_job.map = map_data_asset.to_soft_object_path()

    mrq_preset_data_asset = get_asset_data(args.mrq_preset, "Script/MovieRenderPipelineCore.MoviePipelineMasterConfig")
    unreal.log(f"Setting the movie pipeline preset to `{mrq_preset_data_asset.asset_name}`")
    render_job.set_configuration(mrq_preset_data_asset.get_asset())

    # output directory settings
    outputSetting = render_job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    outputSetting.output_directory.set_editor_property("path","C:/Renders/SDMP/"+  "{}".format(args.render_out_dir))
    unreal.Paths.combine([outputSetting.output_directory.path, args.render_out_dir, outputSetting.file_name_format])

    unreal.log_warning("These are the project settings {}".format(outputSetting.output_directory.path))

       

    # MRQ added the ability to enable and disable jobs. Check to see is a job is disabled and enable it.
    # The assumption is we want to render this particular job.
    # Note this try/except block is for backwards compatibility
    try:
        if not render_job.enabled:
            render_job.enabled = True
    except AttributeError:
        pass

    try:
        # Execute the render. This will execute the render based on whether its remote or local
        execute_render( is_cmdline=args.cmdline)

    except Exception as err:
        unreal.log_error(f"An error occurred executing the render.\n\tError: {err}")
        raise
