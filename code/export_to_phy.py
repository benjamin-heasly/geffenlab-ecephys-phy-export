import logging
from pathlib import Path

import spikeinterface as si
from spikeinterface.exporters import export_to_phy


def export_phy(
    results_path: Path,
    postprocessed_path: Path,
    curated_path: Path,
    compute_pc_features: bool,
    copy_binary: bool,
    n_jobs: int
) -> Path:
    """Export AIND ecephys sorting results from SpikeInterface to Phy."""

    logging.info(f"Loading postprocessed sorting data: {postprocessed_path}")
    sorting_analyzer = si.load_sorting_analyzer(postprocessed_path)
    logging.info(sorting_analyzer)

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
