import logging
from pathlib import Path
import json
from contextlib import chdir


import numpy as np
import spikeinterface as si
from spikeinterface.exporters import export_to_phy
from spikeinterface.core import compute_sparsity


def find_deepest_recording(recording_dict: dict):
    """Parse SpikeInterface recording metadata to find the innermost, base recording."""
    kwargs = recording_dict.get("kwargs")
    if isinstance(kwargs, dict):
        nested = kwargs.get("parent_recording", kwargs.get("recording", None))
        if isinstance(nested, dict):
            return find_deepest_recording(nested)
    return recording_dict


def export_phy(
    results_path: Path,
    probe_path: Path,
    preprocessed_path: Path,
    postprocessed_path: Path,
    curated_path: Path,
    sparsity_radius_um: float,
    compute_pc_features: bool,
    pc_n_components: int,
    pc_mode: str,
    copy_binary: bool,
    n_jobs: int
) -> Path:
    """Export ecephys sorting results from SpikeInterface to Phy."""

    logging.info(f"Loading recording filter config from preprocessing path: {preprocessed_path}")
    with open(preprocessed_path, 'r') as f:
        recording_dict = json.load(f)

    base_recording_dict = find_deepest_recording(recording_dict)

    # Work around a known bug in SpikeInterface, if needed:
    #   https://github.com/SpikeInterface/spikeinterface/issues/4109
    # SpikeInterface can use a PhaseShiftRecording and "inter_sample_shift" data to correct probe DAQ multiplexer phase shifting.
    # The source of truth for "inter_sample_shift" should be the original probe metadata (eg SpikeGlx .meta file).
    # However, for older probes, like some NP 2.0 probes, the expected data are not found.
    # Nevertheless, SpikeInterface tries to set up the PhaseShiftRecording.
    # But the PhaseShiftRecording crashes when the "inter_sample_shift" data are not present.
    # SpikeInterface should not try to configure the PhaseShiftRecording when the data are not present!  But it does.
    # We don't need to crash, however.  We can supply dummy data instead, and allow Phy export to continue.
    # We will only do this when the data are missing.  If the data are present, we should be able to proceed happily.
    inter_sample_shift = base_recording_dict['properties'].get('inter_sample_shift', None)
    if inter_sample_shift is None:
        logging.warning(f"Adding placeholder zeros for base recording inter_sample_shift.")
        base_locations = base_recording_dict['properties']['location']
        base_channel_count = len(base_locations)
        base_recording_dict['properties']['inter_sample_shift'] = np.zeros((base_channel_count,))

    # Load the original probe recording along with SpikeInterface filter config.
    # We expect SpikeInterface to look for the original, raw recording in the current directory.
    # So, temporarily change to the probe directory.
    logging.info(f"Loading recording with filter config from probe path: {probe_path}")
    with chdir(probe_path):
        recording = si.load(recording_dict, base_folder=probe_path)
    logging.info(recording)

    # Load the spike sorting results from SpikeInterface.
    logging.info(f"Loading sorting results from postprocessing path: {postprocessed_path}")
    sorting_analyzer = si.SortingAnalyzer.load(postprocessed_path, recording)
    logging.info(sorting_analyzer)
    logging.info(f"Sorting analyzer has recording: {sorting_analyzer.has_recording()}")

    # Include SpikeInterface auto-curation results in the export to Phy.
    logging.info(f"Loading auto-curating results from curated path: {curated_path}")
    sorting_curated = si.load(curated_path)
    logging.info(sorting_curated)

    logging.info(f"Computing sparstiy with radius {sparsity_radius_um} microns.")
    new_sparsity = compute_sparsity(sorting_analyzer, method="radius", radius_um=sparsity_radius_um)
    sorting_analyzer.sparsity = new_sparsity

    curated_properties = sorting_curated.get_property_keys()
    for property_name in curated_properties:
        logging.info(f"Adding cluster property: {property_name}")
        property_values = sorting_curated.get_property(property_name)
        sorting_analyzer.set_sorting_property(property_name, property_values)

    logging.info(f"compute_pc_features {compute_pc_features}")
    if compute_pc_features:
        logging.info(f"PC features with n_components {pc_n_components}, mode {pc_mode}")
        sorting_analyzer.compute(
            "principal_components",
            n_components=pc_n_components,
            mode=pc_mode,
            n_jobs=n_jobs
        )

    # Export all of the above to Phy format.
    phy_path = Path(results_path, "phy", postprocessed_path.stem)
    logging.info(f"Exporting to Phy: {phy_path}")
    logging.info(f"copy_binary {copy_binary}")
    with chdir(probe_path):
        export_to_phy(
            sorting_analyzer=sorting_analyzer,
            output_folder=phy_path,
            additional_properties=curated_properties,
            remove_if_exists=True,
            copy_binary=copy_binary,
            n_jobs=n_jobs
        )

    return phy_path
