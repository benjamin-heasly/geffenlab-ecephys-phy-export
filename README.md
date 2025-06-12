# geffenlab-ecephys-phy-export

This capsule reads results from the [aind-ephys-pipeline (kilosort4)](https://codeocean.allenneuraldynamics.org/capsule/9352933/tree) pipeline and exports data for use with [Phy](https://github.com/cortex-lab/phy).

# data

The aind-ephys-pipeline `postprocessed/` data are required, as in [ecephys_AS20_2025-03-11_11-08-51_v2_sorted
](https://codeocean.allenneuraldynamics.org/data-assets/42ee2286-92cf-4323-8c65-fe25ef8b1ed6/ecephys?filters=N4Igzg9gTgLiBcIDGUCmBDGqAmIA0I2qYSCMUArqgQA7oDmqCAjLalAAoNPwBMADAXTYAbugB2SHAmABfAgFsKAGxgBLAGJrV7MDJDokUsGAAyqEamV74AbWRpM0gLqzZQA).  The data asset should be attached to the capsule at `/data`.

The raw session data assed (the same used as input to aind-ephys-pipeline) is optional, as in [ecephys_AS20_2025-03-11_11-08-51_v2
](https://codeocean.allenneuraldynamics.org/data-assets/2429fd9e-80c5-4cf0-a281-9c8043cfc402/ecephys?filters=N4Igzg9gTgLiBcIDGUCmBDGqAmIA0I2qYSCMUArqgQA7oDmqCAjLalAAoNPwBMADAXTYAbugB2SHAmABfAgFsKAGxgBLAGJrV7MDJDokUsGAAyqEamV74AbWRpM0gLqzZQA).  If this asset is also attached to the capsule at `/data` then the capsule can optionally export:

 - PC features to support the Phy feature view (use `--compute-pc-features True`)
 - a filtered copy of the original ap recording binary (use `--copy-binary True`)

PC features and copy binary are optional.