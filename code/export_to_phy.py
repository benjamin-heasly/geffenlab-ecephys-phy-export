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
    postprocessed_path = list(data_path.glob(postprocessed_pattern))[0]
    logging.info(f"Loading postprocessed sorting data: {postprocessed_path}")

    sorting_analyzer = si.load_sorting_analyzer(postprocessed_path)
    logging.info(sorting_analyzer)

    curated_paths = list(data_path.glob(curated_pattern))
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


    phy_path = Path(results_path, "phy", postprocessed_path.stem)
    logging.info(f"Exporting to Phy: {phy_path}")
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
