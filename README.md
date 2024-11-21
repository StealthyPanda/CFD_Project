# Analysis of Flow around Streamline bodies

This project uses OpenFOAM v2212 and Python 3.12.6 for analysis around streamline bodies, generated from 2D profiles using extrusion or revolution (sweep).

- [curve_to_model.py](./curve_to_model.py) has methods and functions to generate 3D STL objects from curves.
- [odin.py](./odin.py) is the automation script that takes in input from [odinconfig.json](./odinconfig.json) file. This file contains all the input needed like the models to use, the block sizes etc. The script creates a new case for each of these combinations, and runs them automatically.
- [yplus.py](./yplus.py) contains a simple script to get all the $y^{+}_{min}$ values from all the cases and plots them.

The `_template` case is used as the template, and contains all the common global settings and parameters.

This analysis was originally run using 12 (3, 2, 2) hierarchical subdomains, on a 12th Gen Intel(R) Core(TM) i7-12700H @ 4.6GHz and it took about ~1.2 Hrs for a domain with $10^5$ blocks.

This repo can be adapted to run on HPCs by changing the subdomain settings in `_template` case.
