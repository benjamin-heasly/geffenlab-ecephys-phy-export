import sys
import logging
from pathlib import Path

from export_to_phy import export_phy
from create_cluster_info import create_cluster_info


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# TODO: argparse the args, add a main() function.
phy_path = export_phy(
    data_path=Path("/data"),
    results_path=Path("/results"),
    postprocessed_pattern="**/postprocessed/block0_imec0.ap_recording1.zarr",
    curated_pattern="**/curated/block0_imec0.ap_recording1/",
    compute_pc_features=False,
    copy_binary=False,
    n_jobs= -1
)

params_py = Path(phy_path, "params.py")
create_cluster_info(params_py)
