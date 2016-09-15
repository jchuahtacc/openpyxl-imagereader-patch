# openpyxl-imagereader-patch

`openpyxl` patch to support reading of images in `.xlsx` files

### Introduction

This patches the `openpyxl` Python package, available at [https://bitbucket.org/openpyxl/openpyxl/src](https://bitbucket.org/openpyxl/openpyxl/src). The current implementation (2.4.x as of September 15th, 2016) does not support reading images from `.xlsx` files. (It does support embedding images in cells and writing them, but not reading them.)

This code is derived from a [gist](https://gist.github.com/pikhovkin/543709a2e2827d9c345d) written by [Sergey Pikhovkin](https://gist.github.com/pikhovkin) intended to apply the same functionality. However, the original gist was written for `openpyxl` 2.1.2 and is no longer compatible. Thus, this patch is intended to update the original patch to be compatible with `openpyxl` 2.4.x.
