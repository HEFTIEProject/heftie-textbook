from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import numpy.typing as npt
import zarr
import zarr.storage


def load_heart_data(array_type: Literal["numpy", "zarr"]):
    data_path = (Path(__file__).parent / "data" / "hoa_heart.zarr").resolve()
    if not data_path.exists():
        raise FileNotFoundError(f"{data_path} does not exist.")

    arr_zarr = zarr.open_array(store=data_path, mode="r")
    if array_type == "numpy":
        return np.array(arr_zarr[:])
    elif array_type == "zarr":
        return arr_zarr
    else:
        raise ValueError(f"Did not recognise {array_type=}")


def plot_slice(array: npt.ArrayLike, *, z_idx: int, ax: Axes | None = None) -> None:
    if ax is None:
        _, ax = plt.subplots()
    ax.imshow(array[:, :, z_idx], cmap="Grays_r")
    ax.set_title(f"Slice at z={z_idx}")
    ax.axis("off")


def get_directory_contents(dirpath: Path) -> list[str]:
    if not dirpath.is_dir():
        raise ValueError(f"{dirpath} is not a directory")

    return sorted(d.relative_to(dirpath).name for d in dirpath.glob("*"))
