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
authors:
  - id: dstansby
---

# Appendices

## OME-Zarr creation libraries

A number of libraries exist for creating OME-Zarr datasets from existing data.
This table lists them, and drawbacks when working with 3D imaging data.

| Library                                                   | Drawbacks                                                                                                     |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [ome-zarr-py](https://github.com/ome/ome-zarr-py)         | Not able to correctly downsample 3D images (see [issue #262](https://github.com/ome/ome-zarr-py/issues/262)). |
| [ngff-zarr ](https://ngff-zarr.readthedocs.io/en/stable/) |                                                                                                               |
