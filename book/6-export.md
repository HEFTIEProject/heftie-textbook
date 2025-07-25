---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Exporting

+++

In this chapter we'll look at how to convert sub-volumes of 3D zarr images to other file formats.
The use case for this is allow users to extract sub-volumes of large 3D images into a preferred file format, perform some analysis/processing on the sub-volume using their preferred tools and then copy the results back in-place to the original zarr image.


```{code-cell} ipython3
import napari

import nibabel as nib
import pydicom
from pydicom.dataset import Dataset, FileDataset
import datetime
```

## Converting Zarr sub-volumes to tiff

To begin this chapter, we'll look at how to convert Zarr sub-volumes to tiff.

To start with we'll load our heart sample dataset, as a zarr array and then extract a smaller volume as a NumPy array.

Note: the heart sample dataset is only 200MB, so the entire dataset could be extracted into a NumPy array (and therefore loaded into memory) if required.
If you are working with larger datasets, you will need to keep the extracted volume small enough to fit into memory, or extract it as a series of smaller chunks.

```{code-cell} ipython3
from pathlib import Path
import zarr
import numpy as np

data_path: data_path = (Path(__file__).parent / "data" / "hoa_heart.zarr").resolve()
zarr_array = zarr.open_array(data_path)
slc = [slice(100, 200), slice(100, 200), slice(100, 200)]
np_array = zarr_array[slc]
n_bytes = np_array.nbytes  
n_gb = n_bytes / (10**9)
# Print store information to show data is not loaded into memory
print(f"Zarr array store: {zarr_array.store}")
print(f"Zarr array shape: {zarr_array.shape}")
print(f"Zarr array dtype: {zarr_array.dtype}")
print(f"Zarr array chunks: {zarr_array.chunks}")
print(f"Sub-volume size: {n_gb:.3f} GB")
print(f"Only the requested slice is loaded into memory as a NumPy array")
```

The next step is to write this NumPy array to a tiff file.
We'll use the `imageio` library to do this.

Processing of the sub-volume can be done using any tool that can read and write tiff files.
For example, you could use `Napari`.

The `imageio` library is used to then read the tiff file back into a NumPy array.
This subvolume array can then be copied back in place to the original Zarr array.

```{code-cell} ipython3
import imageio.v3 as iio
iio.imwrite("image_file.tiff", np_array, plugin='tifffile')

# Do some processing with another tool / software here...
# Then load the result:
sub_array = iio.imread("image_file.tiff", plugin='tifffile')

zarr_array[100:200, 100:200, 100:200]=zarr_small


```

To view the results, we can use the `napari` viewer to display the Zarr array including the newly written sub-volume.

```{code-cell} ipython3
viewer = napari.Viewer()
new_layer = viewer.add_image(zarr_array)
napari.run()
```

+++




Both the NIfTI and DICOM sub-volumes can be viewed in open-source viewers such as `ITK-SNAP` (see [ITK-SNAP site](https://www.itksnap.org/pmwiki/pmwiki.php)).

Note: This process is more complex for OME-Zarr images that have a series of different resolution levels.
When writing the processed sub-volume back to the OME-Zarr image, you will need to ensure that the resolution levels are updated correctly.
