# Adaptive 2D/3D Observation-System Research Code

This repository contains research code for designing and evaluating adaptive observation systems in two- and three-dimensional velocity models. The workflow covers first-arrival travel-time calculation, receiver and calibration-source selection, source localization, uncertainty calibration, robustness analysis, and localization/migration comparisons.

The original implementation is preserved in the single main script:

`Final_observation_system_adaptive_2D_3D_complete.py`

## Main features

- Calculates first-arrival travel times on 2D and 3D velocity grids. When `scikit-fmm` is installed, the code uses the Fast Marching Method (FMM).
- Compares multiple receiver-layout and source-localization methods.
- Evaluates spatially correlated velocity perturbations, picking noise, confidence-interval coverage, and tail risk.
- Supports joint receiver and calibration-source design with independent training, interval-calibration, validation, and test splits.
- Writes research outputs as CSV, JSON, NumPy arrays, MATLAB-compatible files, and PNG figures.
- Contains optional legacy Devito RTM helpers. The active fast PSDM workflow does not require Devito.

## Repository layout

```text
.
├── Final_observation_system_adaptive_2D_3D_complete.py  # Main program
├── README.md                                            # Documentation
├── requirements.txt                                     # Main dependencies
├── requirements-optional.txt                            # Optional Devito dependency
├── tests/
│   └── test_quick.py                                    # Fast, data-free tests
└── .gitignore
```

## Requirements

- Python 3.10 or later
- A dedicated virtual environment is recommended
- Full experiments may require substantial CPU time, memory, and disk space

Create an environment and install the main dependencies.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install the optional dependency only if the legacy Devito RTM helpers are required:

```bash
python -m pip install -r requirements-optional.txt
```

## Run the quick tests

Two levels of testing are available.

### Fast, data-free checks

These tests do not start the full optimization workflow or require a velocity file. They import the main module and check:

- expected workflow entry points;
- travel-time calculation on a small 2D grid;
- positive definiteness of the correlated-noise covariance matrix; and
- the stable Cholesky implementation.

Run the tests from the repository root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

A successful run executes three tests and ends with `OK`.

### Quick Marmousi workflow test

To test the executable research workflow, place a Marmousi velocity file named `marmousi.bin` in the repository root. The file must contain `681 × 141` native `float32` values in NumPy C order.

The code defaults to `Marmousi_2D`, reads `./marmousi.bin`, and uses `ROBUST_COMPUTE_PROFILE=quick`. The profile is set explicitly below so the selected test scale is visible and reproducible.

Windows PowerShell:

```powershell
$env:ROBUST_COMPUTE_PROFILE = "quick"
python .\Final_observation_system_adaptive_2D_3D_complete.py
```

Linux or macOS:

```bash
ROBUST_COMPUTE_PROFILE=quick \
python Final_observation_system_adaptive_2D_3D_complete.py
```

This integration test writes its results to the default `output_images` directory. It runs the actual Marmousi design and validation workflow and is therefore much slower than the three unit tests.

## Recommended first run

The program is configured through environment variables rather than command-line arguments. Its current defaults are:

- `MODEL_TYPE=Marmousi_2D`;
- `MARMOUSI_VELOCITY_FILE=./marmousi.bin`;
- `ROBUST_COMPUTE_PROFILE=quick`; and
- `OUTPUT_DIR=output_images`.

Copy the `681 × 141` float32 Marmousi file to the repository root as `marmousi.bin`, then run the following command. The explicit variables document the experiment and place its products in a dedicated output directory.

### Windows PowerShell

```powershell
$env:MODEL_TYPE = "Marmousi_2D"
$env:MARMOUSI_VELOCITY_FILE = ".\marmousi.bin"
$env:ROBUST_COMPUTE_PROFILE = "quick"
$env:OUTPUT_DIR = "output_images\marmousi_quick"
python .\Final_observation_system_adaptive_2D_3D_complete.py
```

### Linux or macOS

```bash
MODEL_TYPE=Marmousi_2D \
MARMOUSI_VELOCITY_FILE=./marmousi.bin \
ROBUST_COMPUTE_PROFILE=quick \
OUTPUT_DIR=output_images/marmousi_quick \
python Final_observation_system_adaptive_2D_3D_complete.py
```

Because these values match the code defaults except for the dedicated output directory, the minimal equivalent command is simply:

```bash
python Final_observation_system_adaptive_2D_3D_complete.py
```

Results are written below `OUTPUT_DIR`. The `quick` profile is a complete research workflow, not a unit-test shortcut: it performs receiver design, independent velocity-split generation, localization comparisons, interval calibration, bootstrap analysis, evidence generation, and plotting.

## Model selection

Set `MODEL_TYPE` to one of the following values:

| Value | Dimensions | Velocity data | Grid shape |
|---|---:|---|---:|
| `Anomaly_2D` | 2D | Built into the program | `81 × 61` |
| `Anomaly_3D` | 3D | Built into the program | `41 × 41 × 31` |
| `Marmousi_2D` (default) | 2D | External float32 binary file | `681 × 141` |
| `SEAM_3D` | 3D | External float32 binary file | `50 × 75 × 75` |

### Marmousi example

```powershell
$env:MODEL_TYPE = "Marmousi_2D"
$env:MARMOUSI_VELOCITY_FILE = "D:\data\marmousi.bin"
$env:OUTPUT_DIR = "output_images\marmousi"
python .\Final_observation_system_adaptive_2D_3D_complete.py
```

### SEAM example

```powershell
$env:MODEL_TYPE = "SEAM_3D"
$env:SEAM_VELOCITY_FILE = "D:\data\seam.bin"
$env:OUTPUT_DIR = "output_images\seam"
python .\Final_observation_system_adaptive_2D_3D_complete.py
```

An external velocity file must contain a native `float32` array with exactly the number of elements required by the selected grid. The program reshapes it using NumPy C order.

## Frequently used environment variables

| Variable | Default | Purpose |
|---|---|---|
| `MODEL_TYPE` | `Marmousi_2D` | Selects the velocity model |
| `OUTPUT_DIR` | `output_images` | Selects the output directory |
| `ADD_WELL_SENSORS` | `1` | Enables borehole candidate receivers |
| `ROBUST_COMPUTE_PROFILE` | `quick` | Selects `smoke`, `quick`, `balanced`, or `production` |
| `ROBUST_TWIN_TEST_MODE` | `0` | Forces the smoke profile when set to `1` |
| `ROBUST_RECEIVER_COUNT` | Calculated internally | Sets the number of deployed receivers |
| `ROBUST_PARALLEL_WORKERS` | CPU-dependent | Sets the number of velocity-model worker processes |
| `RUN_MAIN_MODEL_ADVANTAGE_EVIDENCE` | `1` | Enables additional main-model evidence figures |
| `RUN_FAST_PSDM` | Inherits `RUN_DEVITO_RTM`; enabled by default | Enables the fast PSDM stage |
| `SAVE_MATLAB_TEXT_DATA` | `0` | Enables additional MATLAB/text output |

Fine-grained controls are defined in `reviewer_analysis_config()` and `robust_closed_loop_config()` in the main script.

## Code-analysis notes

- The source is a large, monolithic research script containing more than 300 top-level functions and 10 top-level classes. It is better treated as a reproducible experiment program than as a stable public Python API.
- Importing the module changes global Matplotlib settings and wraps `Figure.savefig`. Embedding it in another plotting application can therefore affect figures created elsewhere in the same process.
- Without `scikit-fmm`, travel-time calculation falls back to a homogeneous Euclidean-distance approximation based on the mean velocity. This permits execution but is not scientifically equivalent to the FMM result.
- An unrecognized `MODEL_TYPE` value falls through to the `Anomaly_2D` branch, so the spelling should be checked carefully.
- The default `quick` profile still contains multiple independent velocity realizations and events. Use `smoke` for a smaller diagnostic run on a resource-constrained machine.
- Velocity-arrival checkpoints can be reused between runs. Use a separate `OUTPUT_DIR` after changing physical or experimental parameters to avoid mixing incompatible results.

## License

No open-source license has been added automatically. Only the code's rights holder can decide whether and how to license it for third-party use. After ownership is confirmed, an appropriate license such as MIT, BSD-3-Clause, or GPL-3.0 may be added at the repository root.
