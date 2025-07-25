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
import os
import pydicom
from pydicom.dataset import Dataset, FileDataset
import datetime

# Create output folder
output_folder = "dicom_slices_robust"
os.makedirs(output_folder, exist_ok=True)

# Get a subset of the 3D array (slices 100-200)
np_array_subset = zarr_array[100:200, :, :]
print(f"Processing {np_array_subset.shape[0]} slices (100-200)...")
print(f"Original data type: {np_array_subset.dtype}")

# Normalise the data
if np_array_subset.dtype == np.float32 or np_array_subset.dtype == np.float64:
    # For float data, normalize and convert to uint16
    data_min = float(np_array_subset.min())
    data_max = float(np_array_subset.max())
    print(f"Data range: {data_min} to {data_max}")
    
    if data_max > data_min:
        np_array_normalized = ((np_array_subset - data_min) / (data_max - data_min) * 65535).astype(np.uint16)
    else:
        np_array_normalized = np.zeros_like(np_array_subset, dtype=np.uint16)
else:
    # For integer data, just convert to uint16
    np_array_normalized = np_array_subset.astype(np.uint16)

# Generate unique UIDs
study_uid = pydicom.uid.generate_uid()
series_uid = pydicom.uid.generate_uid()

# Define spacing and origin
pixel_spacing = [0.2, 0.2]  # Adjust based on your actual pixel spacing
slice_thickness = 0.2       # Adjust based on your actual slice thickness
origin = [0.0, 0.0, 0.0]

for i in range(100):
    # Get 2D slice
    data_2D = np_array_normalized[i, :, :]
    
    # Ensure data is contiguous
    data_2D = np.ascontiguousarray(data_2D)
    
    # Create file metadata
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = pydicom.uid.generate_uid()
    file_meta.ImplementationVersionName = "PYDICOM_1.0"
    
    ds = FileDataset(f"slice_{i+100:04d}.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # Patient Module
    ds.PatientName = "Zarr^Patient"
    ds.PatientID = "ZP001"
    ds.PatientBirthDate = "19900101"
    ds.PatientSex = "O"
    
    # General Study Module
    ds.StudyInstanceUID = study_uid
    ds.StudyID = "1"
    ds.StudyDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.StudyTime = datetime.datetime.now().strftime("%H%M%S")
    ds.AccessionNumber = "ACC001"
    ds.ReferringPhysicianName = "Dr^Referring"
    
    # General Series Module
    ds.SeriesInstanceUID = series_uid
    ds.SeriesNumber = 1
    ds.Modality = "CT"
    ds.SeriesDescription = "Zarr Volume Series"
    ds.SeriesDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.SeriesTime = datetime.datetime.now().strftime("%H%M%S")
    
    # General Equipment Module
    ds.Manufacturer = "Zarr Tools"
    ds.ManufacturerModelName = "ZarrConverter"
    ds.SoftwareVersions = "1.0"
    
    # Frame of Reference Module
    ds.FrameOfReferenceUID = pydicom.uid.generate_uid()
    ds.PositionReferenceIndicator = ""
    
    # General Image Module
    ds.InstanceNumber = i + 1
    ds.PatientOrientation = ""
    ds.ImageDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.ImageTime = datetime.datetime.now().strftime("%H%M%S")
    ds.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]
    ds.AcquisitionNumber = 1
    ds.AcquisitionDate = datetime.datetime.now().strftime("%Y%m%d")
    ds.AcquisitionTime = datetime.datetime.now().strftime("%H%M%S")
    
    # Image Plane Module (Critical for 3D reconstruction)
    ds.SliceThickness = str(slice_thickness)
    ds.SpacingBetweenSlices = str(slice_thickness)
    ds.SliceLocation = float(i * slice_thickness)
    ds.ImagePositionPatient = [
        float(origin[0]), 
        float(origin[1]), 
        float(origin[2] + i * slice_thickness)
    ]
    ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    
    # Image Pixel Module
    ds.Rows = data_2D.shape[0]
    ds.Columns = data_2D.shape[1]
    ds.PixelSpacing = [float(pixel_spacing[0]), float(pixel_spacing[1])]
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.SamplesPerPixel = 1
    
    # CT Image Module (if using CT modality)
    ds.RescaleIntercept = "0"
    ds.RescaleSlope = "1"
    ds.RescaleType = "HU"
    
    # SOP Common Module
    ds.SOPClassUID = pydicom.uid.CTImageStorage  # Match file_meta
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    
    # Set pixel data
    ds.PixelData = data_2D.tobytes()
    
    # Validate dataset
    ds.is_implicit_VR = False
    ds.is_little_endian = True
    
    # Save file
    output_path = os.path.join(output_folder, f"slice_{i+100:04d}.dcm")
    ds.save_as(output_path, write_like_original=False)
    
    if i % 10 == 0:
        print(f"Saved slice {i+100}")

print(f"100 slices (100-199) saved to '{output_folder}' folder")
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
