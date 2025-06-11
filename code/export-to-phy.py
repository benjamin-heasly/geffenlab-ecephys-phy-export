import spikeinterface as si
from spikeinterface.exporters import export_to_phy

# pattern to match block0_imec0
# configureable /data

# pattern to locate .zarr
postprocessed_dir = "/data/ecephys/postprocessed/block0_imec0.ap_recording1.zarr/"
sorting_analyzer = si.load_sorting_analyzer(postprocessed_dir)
print(sorting_analyzer)

# pattern to locate curated dir
curated_dir = "/data/ecephys/curated/block0_imec0.ap_recording1/"
sorting_curated = si.load(curated_dir)
curated_properties = sorting_curated.get_property_keys()
for property_name in curated_properties:
  property_values = sorting_curated.get_property(property_name)
  sorting_analyzer.set_sorting_property(property_name, property_values)

# configurable /results
# results subdir like recording json?
# option to compute_pc_features
phy_dir = "/results/ecephys/phy/"
export_to_phy(
  sorting_analyzer=sorting_analyzer,
  output_folder=phy_dir,
  remove_if_exists=True,
  compute_pc_features=False,
  additional_properties=curated_properties
)

# create cluster_info.tsv
# https://github.com/benjamin-heasly/kilosort3-docker/blob/main/phy/create_cluster_info.py
