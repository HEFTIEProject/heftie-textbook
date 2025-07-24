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

# Converting sub-volumes to/from other file formats

+++

In this chapter we'll look at how to convert sub-volumes of 3D zarr images to and from other file formats.
The use case for this is allow users to extract sub-volumes of large 3D images into a preferred file format,
perform some analysis/processing on the sub-volume using their preferred tools and then
copy the results back in-place to the original zarr image.

Note: this chapter (and the whole of the textbook) uses Zarr version 2 and OME-Zarr version 0.4. Although newer versions exist (Zarr version 3 and OME-Zarr version 0.5), software tools have not quite caught up to support the newer versions.

```{code-cell} ipython3
import napari

import nibabel as nib
import pydicom
from pydicom.dataset import Dataset, FileDataset
import datetime
```

## Converting Zarr sub-volumes to tiff

To begin this chapter, we'll look at how to convert Zarr sub-volumes to tiff.

To start with we'll load our heart sample dataset, as a zarr array
and then extract a smaller volume as a NumPy array.

Note: the heart sample dataset is only 200MB,
so the entire dataset could be extracted into a NumPy array (and therefore loaded into memory) if required.
If you are working with larger datasets, you will need to keep the extracted volume small enough to fit into memory, or extract it as a series of smaller chunks.

```{code-cell} ipython3
from pathlib import Path
import zarr
import numpy as np

data_path: data_path = (Path(__file__).parent / "data" / "hoa_heart.zarr").resolve()
zarr_array = zarr.open_array(data_path)
np_array = zarr_array[100:200, 100:200, 100:200]
n_bytes = 100*100*100*zarr_array.dtype.itemsize  
n_gb = n_bytes / (10**9)
```

The next step is to write this NumPy array to a tiff file.
We'll use the `imageio` library to do this.

Processing of the sub-volume can be done using any tool
that can read and write tiff files.
For example, you could use `Napari`.

The `imageio` library is used to then read the
tiff file back into a NumPy array.
This subvolume array can then be copied back
in place to the original Zarr array.

```{code-cell} ipython3
import imageio.v3 as iio
iio.imwrite("image_file.tiff", np_array, plugin='tifffile')

# Do some processing with another tool / software here...
# Then load the result:
zarr_small=iio.imread("image_file.tiff", plugin='tifffile')

zarr_array[100:200, 100:200, 100:200]=zarr_small


```

To view the results, we can use the `napari` viewer
to display the Zarr array including the newly written sub-volume.

```{code-cell} ipython3
viewer = napari.Viewer()
new_layer = viewer.add_image(zarr_array)
napari.run()
```

+++

## Converting Zarr sub-volumes to NIfTI/DICOM

Next, we'll look at how to convert Zarr sub-volumes to NIfTI and DICOM formats.

To write this sub-volume to a NIfTI file, we can use the `nibabel` library.
After processing the sub-volume, we can then read it back in as a NIfTI image (`nibabel.nifti1.Nifti1Image` class)
to get the image data as a NumPy array
and copy it back in place to the original Zarr array.

```{code-cell} ipython3
nifti_img = nib.Nifti1Image(np_array, affine=np.eye(4))
nib.save(nifti_img, 'output.nii')

# Load the NIfTI file
img = nib.load('output.nii')

# Get the image data as a NumPy array
zarr_small_nii = img.get_fdata()
zarr_array[100:200, 100:200, 100:200]=zarr_small_nii
```

To write this sub-volume to a DICOM file, we can use the `pydicom` library.
Since DICOM is typically used for 2D slices, we
will convert the 3D sub-volume to a 2D NumPy array by taking a single slice.

We then need to create a DICOM dataset and populate it with the necessary metadata using `pydicom.dataset`
where the image data is stored in the `PixelData` attribute.

The `pydicom.dataset.FileDataset` class is then
saved as a DICOM file.


```{code-cell} ipython3
import pydicom
from pydicom.dataset import Dataset, FileDataset
import datetime

# Example 2D data (DICOM is usually 2D per file)
data = np_array[:,:, 0]  # Take the first slice for demonstration

# Create metadata
file_meta = pydicom.Dataset()
ds = FileDataset("output.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)

# Set required values
ds.PatientName = "Test^Patient"
ds.PatientID = "123456"
ds.Modality = "CT"
ds.StudyInstanceUID = "1.2.3"
ds.SeriesInstanceUID = "1.2.3.1"
ds.SOPInstanceUID = "1.2.3.1.1"
ds.SOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

# Set image data
ds.Rows, ds.Columns = data.shape
ds.PhotometricInterpretation = "MONOCHROME2"
ds.SamplesPerPixel = 1
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.PixelData = data.tobytes()

# Save to file
ds.save_as("output.dcm")
```

After processing the sub-volume, we can then read it back in as a DICOM image to get the image data as a NumPy array
and copy it back in place to the original Zarr array.

```{code-cell} ipython3

# Load the DICOM file
ds = pydicom.dcmread('output.dcm')

# Extract the pixel data as a NumPy array
data = ds.pixel_array
```

Both the NIfTI and DICOM sub-volumes can be viewed in open-source viewers such as `ITK-SNAP` (see [ITK-SNAP site](https://www.itksnap.org/pmwiki/pmwiki.php)).

Note: This process is more complex for OME-Zarr images
that have a series of different resolution levels.
When writing the processed sub-volume back to the
OME-Zarr image, you will need to ensure that the
resolution levels are updated correctly.
