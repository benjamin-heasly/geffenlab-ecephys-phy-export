import sys
from argparse import ArgumentParser
from typing import Optional, Sequence, Any
import logging
from pathlib import Path

from export_to_phy import export_phy
from create_cluster_info import create_cluster_info


def set_up_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def capsule_main(
    data_path: Path,
    results_path: Path,
    postprocessed_pattern: str,
    curated_pattern: str,
    compute_pc_features: bool,
    copy_binary: bool,
    n_jobs: int
):

    logging.info("Exporting ecephys sorting results to Phy.\n")
    phy_path = export_phy(
        data_path=data_path,
        results_path=results_path,
        postprocessed_pattern=postprocessed_pattern,
        curated_pattern=curated_pattern,
        compute_pc_features=compute_pc_features,
        copy_binary=copy_binary,
        n_jobs=n_jobs
    )
    logging.info("OK\n")

    logging.info("Creating initial Phy cluster_info.tsv.\n")
    params_py = Path(phy_path, "params.py")
    create_cluster_info(params_py)
    logging.info("OK\n")


def truthy_str(str_value: str) -> bool:
    """Parse a string argument value into a boolean value.

    Using bool as an argparse type doesn't do what we want.
    It gives bool('True') == True, but also bool('False') == True.
    This is becasue 'False' is a non-empty str.
    Likewise for bool('0'), bool('no'), etc.

    BooleanOptionalAction is a nicer, more idiomatic way to handle boolean args.
        https://docs.python.org/3/library/argparse.html#argparse.BooleanOptionalAction
    This sets up mutually exclusive flag arguments like --option vs --no-option.

    But as of writing, Code Ocean App Panels don't support flags like these.
    They only support arguments with explicit values like "--option value".
    So we'll use this function to parse the value into a bool.
    We can set up the App Panel to only pass in values we know how to parse, like "true" or "yes".
    """

    truthy_values = {'true', 't', 'yes', 'y', '1'}
    if str_value.lower() in truthy_values:
        return True
    else:
        return False


def main(argv: Optional[Sequence[str]] = None) -> int:
    set_up_logging()

    parser = ArgumentParser(description="Export ecephys sorting resluts to Phy.")

    parser.add_argument(
        "--data-root", "-d",
        type=str,
        help="Where to find and read input data files. (default: %(default)s)",
        default="/data"
    )
    parser.add_argument(
        "--results-root", "-r",
        type=str,
        help="Where to write output result files. (default: %(default)s)",
        default="/results"
    )
    parser.add_argument(
        "--postprocessed-pattern", "-p",
        type=str,
        help="Glob pattern to locate postprocessed/ dir within DATA_ROOT. (default: %(default)s)",
        default="**/postprocessed/block0_imec0.ap_recording1.zarr"
    )
    parser.add_argument(
        "--curated-pattern", "-c",
        type=str,
        help="Glob pattern to locate curated/ dir within DATA_ROOT. (default: %(default)s)",
        default="**/curated/block0_imec0.ap_recording1/"
    )
    parser.add_argument(
        "--compute-pc-features", "-f",
        type=truthy_str,
        help="True or False, whether to compute pc features for the Phy feature view -- requires the original ap recording binary to be found in DATA_ROOT. (default: %(default)s)",
        default=False
    )
    parser.add_argument(
        "--copy-binary", "-b",
        type=truthy_str,
        help="True or False, whether to write a filtered copy of the ap recording binary into the Phy dir as recording.dat -- requires the original ap recording binary to be found in DATA_ROOT. (default: %(default)s)",
        default=False
    )
    parser.add_argument(
        "--n-jobs", "-n",
        type=int,
        help="Number of jobs to use for parallel processing -- -1 means one job per CPU core. (default: %(default)s)",
        default=-1
    )

    cli_args = parser.parse_args(argv)

    data_path = Path(cli_args.data_root)

    print("DEBUGGING")
    for child in data_path.iterdir():
        print(child)

    results_path = Path(cli_args.results_root)
    try:
        capsule_main(
            data_path=data_path,
            results_path=results_path,
            postprocessed_pattern=cli_args.postprocessed_pattern,
            curated_pattern=cli_args.curated_pattern,
            compute_pc_features=cli_args.compute_pc_features,
            copy_binary=cli_args.copy_binary,
            n_jobs=cli_args.n_jobs
        )
    except:
        logging.error("Error exporting to Phy.", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
