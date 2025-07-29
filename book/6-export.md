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

## Converting Zarr sub-volumes to tiff

To begin this chapter, we'll look at how to convert Zarr sub-volumes to tiff.

To start with we'll load our heart sample dataset, as a zarr array and then extract a smaller volume as a NumPy array.

Note: the heart sample dataset is only 200MB, so the entire dataset could be extracted into a NumPy array (and therefore loaded into memory) if required.
If you are working with larger datasets, you will need to keep the extracted volume small enough to fit into memory, or extract it as a series of smaller chunks.
If you are using an in-memory Zarr store, then the entire dataset will be loaded into memory regardless of the size of the sub-volume you extract.

```{code-cell} ipython3
from pathlib import Path
import zarr
import numpy as np

from data_helpers import load_heart_data, plot_slice
zarr_array = load_heart_data(array_type='zarr')
original_array = zarr_array[:, :, :].copy()  # Copy with original data
changed_array = zarr_array[:, :, :].copy()  # Copy for processed data
start_idx = 400
end_idx = 500
slice_range = slice(start_idx, end_idx)
np_array = zarr_array[slice_range, slice_range, slice_range]
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
For example, you could use `Fiji`.

The `imageio` library is used to then read the tiff file back into a NumPy array.
This subvolume array can then be copied back in place to the original Zarr array.

```{code-cell} ipython3
import imageio.v3 as iio
iio.imwrite("image_file.tiff", np_array, plugin='tifffile')

# Do some processing with another tool / software here e.g. Fiji
# Then load the result:
zarr_small = iio.imread("image_file_processed.tiff", plugin='tifffile')
sub_array = zarr.zeros_like(zarr_small)

original_array[400:500, 400:500, 400:500]=zarr_small

changed_array[slice_range, slice_range, slice_range] = sub_array  # Insert processed data


```

To compare the original and processed sub-volumes, we can visualize them side by side using `matplotlib`.

```{code-cell} ipython3
from data_helpers import plot_slice
import matplotlib.pyplot as plt

fig, axs = plt.subplots(ncols=2)
plot_slice(original_array, z_idx=450, ax=axs[0])
plot_slice(changed_array, z_idx=450, ax=axs[1])
```

+++

## Conversion Format Comparison

The following table summarizes the different file formats for converting Zarr sub-volumes, their associated tools, and trade-offs:

| Format | Tool/Library | Advantages | Disadvantages | Open Source Viewers |
|--------|--------------|------------|---------------|---------------------|
| **TIFF** | [imageio](https://imageio.readthedocs.io/) | • Widely supported<br>• Preserves bit depth<br>• Good for microscopy workflows<br>• Fast read/write | • Limited metadata support<br>• Large file sizes<br>• No compression by default | Napari, ImageJ, Fiji |
| **NIfTI** | [nibabel](https://nipy.org/nibabel/) | • Medical imaging standard<br>• Rich metadata (orientation, spacing)<br>• Good compression<br>• ITK-SNAP, FSL, AFNI support | • Medical imaging specific<br>• Limited to certain data types<br>• Complex coordinate systems | ITK-SNAP, FSL, AFNI |
| **DICOM** | [pydicom](https://pydicom.github.io/) | • Clinical standard<br>• Extensive metadata<br>• Patient/study information<br>• Universal medical viewer support | • Complex format<br>• Large overhead<br>• Requires many mandatory fields<br>• Slow for large volumes | OsiriX, RadiAnt, Horos |
| **NumPy** | [numpy](https://numpy.org/) | • Direct array format<br>• Fast loading<br>• Preserves exact data<br>• Python native | • No metadata<br>• Large file sizes<br>• Python ecosystem only | None (Python only) |

### Recommended Use Cases

- **TIFF**: General imaging workflows, microscopy data, when broad tool compatibility is needed
- **NIfTI**: Medical imaging analysis, neuroimaging studies, when spatial metadata is critical
- **DICOM**: Clinical workflows, when patient metadata is required, for regulatory compliance
- **NumPy**: Quick prototyping, Python-only workflows, temporary data exchange



Both the NIfTI and DICOM sub-volumes can be viewed in open-source viewers such as `ITK-SNAP` (see [ITK-SNAP site](https://www.itksnap.org/pmwiki/pmwiki.php)).

Note: This process is more complex for OME-Zarr images that have a series of different resolution levels.
When writing the processed sub-volume back to the OME-Zarr image, you will need to ensure that the resolution levels are updated correctly.
