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
import plotly.express as px
```

```{code-cell} ipython3
from data_helpers import load_heart_data

heart_image = load_heart_data(array_type='numpy')
```

```{code-cell} ipython3
fig = px.imshow(heart_image, animation_frame=2, binary_string=True)
fig
```

```{code-cell} ipython3

```
