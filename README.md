# pySTC

**pySTC** is a Python interface for Syndrome-Trellis Codes (STC), a method used 
in steganography to minimize embedding distortion when hiding information within 
digital media. STCs are linear convolutional codes represented by a 
parity-check matrix, allowing efficient embedding while preserving the quality 
of the cover medium.

This library is based on the **C++ implementation of Syndrome-Trellis Codes** 
available at [Binghamton University's STC repository](http://dde.binghamton.edu/download/syndrome/). 
We extend our gratitude to the original authors for their contribution to the 
field of steganography.

## Installation

To install **pySTC**, you can use the precompiled binaries available in the `dist` directory. This ensures compatibility and simplifies the installation process. Run the following command:

```bash
pip install dist/pySTC-*.whl
```

Replace * with the appropriate version of the wheel file.

## Usage

Below is an example of how to use pySTC for embedding and extracting messages using Syndrome-Trellis Codes. 
In this example, we have performed the cost calculation using HILL as defined in the paper 
[A New Cost Function for Spatial Image Steganography](https://doi.org/10.1109/ICIP.2014.7025854) 
by Bin Li, Ming Wang, Jiwu Huang and Xiaolong Li.


```python

import pystc
import numpy as np
import imageio.v3 as iio
import warnings
from scipy import signal

warnings.filterwarnings('ignore', category=RuntimeWarning)

input_image = 'image.pgm'

def HILL(I):
    H = np.array(
       [[-1,  2, -1],
        [ 2, -4,  2],
        [-1,  2, -1]])
    L1 = np.ones((3, 3)).astype('float32')/(3**2)
    L2 = np.ones((15, 15)).astype('float32')/(15**2)
    costs = signal.convolve2d(I, H, mode='same')  
    costs = abs(costs)
    costs = signal.convolve2d(costs, L1, mode='same')  
    costs = 1/costs
    costs = signal.convolve2d(costs, L2, mode='same')  
    costs[costs == np.inf] = 1
    return costs

I = iio.imread(input_image)

costs = HILL(I)
seed = 32 # secret seed

message = "Hello World".encode()
stego = pystc.hide(message, I, costs, costs, seed, mx=255, mn=0)

message_extracted = pystc.unhide(stego, seed)
print("Extracted:", message_extracted.decode())

```


## Acknowledgments
Part of the C/C++ code used by HStego comes from the [Digital Data Embedding Laboratory](http://dde.binghamton.edu/download/).
We sincerely appreciate their work in developing and sharing this technology.

These methods are described in the following papers:

- [Minimizing Embedding Impact in Steganography using Trellis-Coded Quantization](https://doi.org/10.1117/12.838002) by Tomas Filler, Jan Judas and Jessica Fridrich.

- [Minimizing Additive Distortion Functions With Non-Binary Embedding Operation in Steganography](https://doi.org/10.1109/WIFS.2010.5711444) by Tomas Filler and Jessica Fridrich.

- [Minimizing Additive Distortion in Steganography using Syndrome-Trellis Codes](https://doi.org/10.1109/TIFS.2011.2134094) by Tomas Filler, Jan Judas and Jessica Fridrich.



## License
This project is licensed under the MIT License. See the [LICENSE](/LICENSE.txt) file for more details.


