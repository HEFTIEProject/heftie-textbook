from pathlib import Path
from typing import Literal
import zarr
import zarr.storage
import numpy as np


def load_heart_data(array_type: Literal["numpy"]):
    arr_zarr = zarr.open_array(
        store=zarr.storage.LocalStore(Path(__file__).parent / "data" / "hoa_heart.zarr")
    )
    if array_type == "numpy":
        return np.asarray(arr_zarr[:])
    else:
        raise ValueError(f"Did not recognise {array_type=}")
