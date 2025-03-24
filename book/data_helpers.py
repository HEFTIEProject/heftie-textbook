from pathlib import Path
from typing import Literal
import zarr
import zarr.storage
import numpy as np


def load_heart_data(array_type: Literal["numpy"]):
    data_path = (Path(__file__).parent / "data" / "hoa_heart.zarr").resolve()
    if not data_path.exists():
        raise FileNotFoundError(f"{data_path} does not exist.")

    arr_zarr = zarr.open_array(store=data_path)
    if array_type == "numpy":
        return np.array(arr_zarr[:])
    else:
        raise ValueError(f"Did not recognise {array_type=}")
