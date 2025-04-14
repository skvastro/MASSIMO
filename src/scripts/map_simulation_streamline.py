import sys
import subprocess

import utils.paths as paths
from maps.map_maker import MapMaker_Parser
from maps.telescope_simulator import TelescopeSimulator
from analysis.bdsf_on_map import bdsf_on_map


def run_mapmaker_on_hopper(map_name, **kwargs):
    # Parse kwargs into command-line argument string
    args = []
    for key, value in kwargs.items():
        if isinstance(value, bool):
            args.append(f"--{key}" if value else "")
        else:
            args.append(f"--{key}={value}")

    remote_command = [
        f"source {paths.MAP_SHELL_SCRIPTS / 'mamba_init.sh'}",
        f"cd {paths.BASE_PARENT}/src",
        f"micromamba activate /hs/fs08/data/group-brueggen/tmartinez/envs/cenv_diffusion",
        f"python -m maps.map_maker "
        + " ".join(args)
        + (" " if len(args) else "")
        + f"{map_name}",
    ]
    cmd = f"ssh hopper '/bin/bash -l -c \"{' && '.join(remote_command)}\"'"
    print(f"Running command: {cmd}")

    with subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    ) as proc:
        for line in proc.stdout:
            print(line, end="")

def run_telsim_loca(map_name):
    command = [
        f"source {paths.MAP_SHELL_SCRIPTS / 'mamba_init.sh'}",
        f"cd {paths.BASE_PARENT}/src",
        f"micromamba activate /hs/fs08/data/group-brueggen/tmartinez/envs/cenv_diffusion",
        f"python -m maps.telescope_simulator {map_name}",
    ]


if __name__ == "__main__":
    # Parse command line arguments
    parser = MapMaker_Parser()
    args = parser.parse_args()
    map_name = args.map_name

    # Run mapmaker on hopper
    run_mapmaker_on_hopper(map_name, **vars(args))

    # Run telescope simulator locally
    ts = TelescopeSimulator(map_name)
    ts.run()

    # Run the analysis
    map_file = (
        paths.SKY_MAP_PARENT / map_name / 'ddf' / f"{map_name}.int.restored.fits"
    )
    bdsf_on_map(map_file)

    # TO DO: Streamline analysis of stats


