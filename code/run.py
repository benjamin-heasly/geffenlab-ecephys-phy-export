import sys
from argparse import ArgumentParser
from typing import Optional, Sequence
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


def first_match(
    pattern: str,
    candidates: list[str]
) -> str:
    for candidate in candidates:
        if pattern in str(candidate):
            return candidate
    return None


def capsule_main(
    processed_data_path: Path,
    preprocessed_pattern: str,
    postprocessed_pattern: str,
    curated_pattern: str,
    ecephys_path: Path,
    ecephys_probe_delimiter: str,
    ecephys_probe_names: list[str],
    results_path: Path,
    sparsity_radius_um: float,
    compute_pc_features: bool,
    pc_n_components: int,
    pc_mode: str,
    copy_binary: bool,
    n_jobs: int
):
    logging.info(f"Exporting sorting results to Phy at: {results_path}.")
    logging.info(f"Searching for processed data from: {processed_data_path}.")
    logging.info(f"Searching for raw ecephys data from: {ecephys_path}.")

    # Locate SpikeInterface preprocessed, postprocessed, and curated results.
    logging.info(f"Looking for preprocessed/ paths(s) matching: {preprocessed_pattern}")
    preprocessed_paths = list(processed_data_path.glob(preprocessed_pattern))
    preprocessed_count = len(preprocessed_paths)
    logging.info(f"Found {preprocessed_count} preprocessed data paths: {preprocessed_paths}")

    logging.info(f"Looking for postprocessed/ paths(s) matching: {postprocessed_pattern}")
    postprocessed_paths = list(processed_data_path.glob(postprocessed_pattern))
    postprocessed_count = len(postprocessed_paths)
    logging.info(f"Found {postprocessed_count} postprocessed data paths: {postprocessed_paths}")

    logging.info(f"Looking for curated/ paths(s) matching: {curated_pattern}")
    curated_paths = list(processed_data_path.glob(curated_pattern))
    curated_count = len(curated_paths)
    logging.info(f"Found {curated_count} curated data paths: {curated_paths}")

    # Locate ecephys probe subdirs.
    logging.info(f"Searching for probe path(s) within: {ecephys_path}")
    probe_paths = [subdir for subdir in ecephys_path.iterdir() if subdir.is_dir()]
    probe_count = len(probe_paths)
    logging.info(f"Found {probe_count} probe paths: {probe_paths}")

    # Decide which probes to convert.
    if ecephys_probe_names:
        logging.info(f"Using the given probe names: {ecephys_probe_names}")
    else:
        ecephys_probe_names = [subdir.name.split(ecephys_probe_delimiter)[-1] for subdir in probe_paths]
        logging.info(f"Found probe names: {ecephys_probe_names}")

    # Convert each probe, combining raw ecephys data and SpikeInterface processing results.
    for probe_name in ecephys_probe_names:
        logging.info(f"Exporting probe: {probe_name}")

        probe_path = first_match(probe_name, probe_paths)
        if not probe_path:
            logging.warning(f"Skipping probe {probe_name}, no matching prove path found.")
            continue

        probe_path = first_match(probe_name, probe_paths)
        if not probe_path:
            logging.warning(f"Skipping probe {probe_name}, no matching prove path found.")
            continue

        preprocessed_path = first_match(probe_name, preprocessed_paths)
        if not preprocessed_path:
            logging.warning(f"Skipping probe {probe_name}, no matching preprocessed path found.")
            continue

        postprocessed_path = first_match(probe_name, postprocessed_paths)
        if not postprocessed_path:
            logging.warning(f"Skipping probe {probe_name}, no matching postprocessed path found.")
            continue

        curated_path = first_match(probe_name, curated_paths)
        if not curated_path:
            logging.warning(f"Skipping probe {probe_name}, no matching curated path found.")
            continue

        logging.info("Exporting to Phy.")
        logging.info(f"Probe: {probe_path}")
        logging.info(f"Preprocessed: {preprocessed_path}")
        logging.info(f"Posprocessed: {postprocessed_path}")
        logging.info(f"Curated: {curated_path}")
        phy_path = export_phy(
            results_path=results_path,
            probe_path=probe_path,
            preprocessed_path=preprocessed_path,
            postprocessed_path=postprocessed_path,
            curated_path=curated_path,
            sparsity_radius_um=sparsity_radius_um,
            compute_pc_features=compute_pc_features,
            pc_n_components=pc_n_components,
            pc_mode=pc_mode,
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
        "--processed-data-dir", "-P",
        type=str,
        help="Where to search for SpikeInterface preprocessed, postprocesed, and curated results. (default: %(default)s)",
        default="/processed_data"
    )
    parser.add_argument(
        "--preprocessed-pattern", "-p",
        type=str,
        help="Glob pattern to locate preprocessed/ dirs within PROCESSED_DATA_DIR. (default: %(default)s)",
        default="*/*/preprocessed/*.json"
    )
    parser.add_argument(
        "--postprocessed-pattern", "-t",
        type=str,
        help="Glob pattern to locate postprocessed/ dirs within PROCESSED_DATA_DIR. (default: %(default)s)",
        default="*/*/postprocessed/*.zarr"
    )
    parser.add_argument(
        "--curated-pattern", "-c",
        type=str,
        help="Glob pattern to locate curated/ dirs within PROCESSED_DATA_DIR. (default: %(default)s)",
        default="*/*/curated/*/"
    )
    parser.add_argument(
        "--ecephys-dir", "-E",
        type=str,
        help="Where to search for raw ecephys probes and recordings. (default: %(default)s)",
        default="/ecephys"
    )
    parser.add_argument(
        "--ecephys-probe-delimiter", "-d",
        type=str,
        help="Delimiter for parsing ecephys probe subdirectores with names ending like _imec0 or _imec1. (default: %(default)s)",
        default="_"
    )
    parser.add_argument(
        "--ecephys-probe-names", "-N",
        type=str,
        nargs="*",
        help="List of probe namese to look for, for example 'imec0, imec1'.  Omit to search subdirs of ECEPHYS_DIR and parse with ECEPHYS_PROBE_DELIMITER (default: %(default)s)",
        default=None
    )
    parser.add_argument(
        "--results-dir", "-r",
        type=str,
        help="Where to write output result files. (default: %(default)s)",
        default="/results"
    )
    parser.add_argument(
        "--sparsity-radius-um",
        type=float,
        help="Radius in microns for computing sparsity (channel relevance) for exported waveforms, PC features. (default: %(default)s)",
        default=40
    )
    parser.add_argument(
        "--compute-pc-features", "-f",
        type=truthy_str,
        help="True or False, whether to compute and export pc features. (default: %(default)s)",
        default=True
    )
    parser.add_argument(
        "--pc-n-components",
        type=int,
        help="How many PC components to fit. (default: %(default)s)",
        default=3
    )
    parser.add_argument(
        "--pc-mode",
        type=str,
        choices=("by_channel_local", "by_channel_global", "concatenated"),
        help="SpikeInterface PC fit mode. (default: %(default)s)",
        default="by_channel_local"
    )
    parser.add_argument(
        "--copy-binary", "-b",
        type=truthy_str,
        help="True or False, whether to write a filtered copy of the ap recording binary into the Phy dir as recording.dat. (default: %(default)s)",
        default=False
    )
    parser.add_argument(
        "--n-jobs", "-n",
        type=int,
        help="Number of jobs to use for parallel processing -- -1 means one job per CPU core. (default: %(default)s)",
        default=-1
    )

    cli_args = parser.parse_args(argv)
    processed_data_path = Path(cli_args.processed_data_dir)
    ecephys_path = Path(cli_args.ecephys_dir)
    results_path = Path(cli_args.results_dir)
    try:
        capsule_main(
            processed_data_path,
            cli_args.preprocessed_pattern,
            cli_args.postprocessed_pattern,
            cli_args.curated_pattern,
            ecephys_path,
            cli_args.ecephys_probe_delimiter,
            cli_args.ecephys_probe_names,
            results_path,
            cli_args.sparsity_radius_um,
            cli_args.compute_pc_features,
            cli_args.pc_n_components,
            cli_args.pc_mode,
            cli_args.copy_binary,
            cli_args.n_jobs,
        )
    except:
        logging.error("Error exporting to Phy.", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
