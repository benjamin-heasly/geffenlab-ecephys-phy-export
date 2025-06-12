import logging
from pathlib import Path

import spikeinterface as si
from spikeinterface.exporters import export_to_phy


def export_phy(
    data_path: Path,
    results_path: Path,
    postprocessed_pattern: str,
    curated_pattern: str,
    compute_pc_features: bool,
    copy_binary: bool,
    n_jobs: int
) -> Path:
    """Export AIND ecephys sorting results from SpikeInterface to Phy."""
    logging.info(f"Looking for data in: {data_path}")

    # Locate "postprocessed" data from the AIND ecephys pipeline.
    # This includes sorting and quality metrics.
    # It will also find the original ap recording binary, if that data asset is present.
    logging.info(f"Looking for postprocessed/ dir matching: {postprocessed_pattern}")
    #postprocessed_path = list(data_path.glob(postprocessed_pattern))[0]
    postprocessed_path = Path("/data/ecephys_AS20_2025-03-11_11-08-51_v2_sorted/postprocessed/block0_imec0.ap_recording1.zarr")
    logging.info(f"Loading postprocessed sorting data: {postprocessed_path}")
    sorting_analyzer = si.load_sorting_analyzer(postprocessed_path)
    logging.info(sorting_analyzer)

    # Locate optional "curated" data from the AIND ecephys pipeline.
    # This includes automatic cluster labeling based on qualtiy metrics.
    logging.info(f"Looking for curated/ dir matching: {curated_pattern}")
    curated_paths = list(data_path.glob(curated_pattern))
    curated_path = [Path("/data/ecephys_AS20_2025-03-11_11-08-51_v2_sorted/curated/block0_imec0.ap_recording1")]
    curated_properties = []
    if curated_paths:
        curated_path = curated_paths[0]
        logging.info(f"Loading auto-curating results: {curated_path}")

        sorting_curated = si.load(curated_path)
        logging.info(sorting_curated)

        curated_properties = sorting_curated.get_property_keys()
        for property_name in curated_properties:
            logging.info(f"Adding cluster property: {property_name}")
            property_values = sorting_curated.get_property(property_name)
            sorting_analyzer.set_sorting_property(property_name, property_values)

    # Export from SpikeInterface format to Phy format.
    # This can copy a filtered version of the ap recording binary, if that data asset is present. 
    phy_path = Path(results_path, "phy", postprocessed_path.stem)
    logging.info(f"Exporting to Phy: {phy_path}")
    logging.info(f"compute_pc_features {compute_pc_features}")
    logging.info(f"copy_binary {copy_binary}")
    export_to_phy(
        sorting_analyzer=sorting_analyzer,
        output_folder=phy_path,
        additional_properties=curated_properties,
        remove_if_exists=True,
        compute_pc_features=compute_pc_features,
        copy_binary=copy_binary,
        n_jobs=n_jobs
    )

    return phy_path
