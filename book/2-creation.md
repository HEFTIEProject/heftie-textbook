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

# Creating chunked datasets

```{code-cell} ipython3
import matplotlib.pyplot as plt

from data_helpers import load_heart_data
```

```{code-cell} ipython3
heart_image = load_heart_data(array_type='numpy')
```

```{code-cell} ipython3
fig, ax = plt.subplots()
ax.imshow(heart_image[:, :, 70], cmap='Grays_r')
ax.set_title("z = 70")
```
