# Path-Correlated-Travel-Time-Discrepancy-and-Joint-Observation-System-Design
a closed-loop framework that retains a fixed reference velocity model while learning empirical travel-time corrections from independent velocity realizations and observations at known calibration sources.

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

The quick tests do not start the full optimization workflow or generate large output files. They import the main module and check:

- expected workflow entry points;
- travel-time calculation on a small 2D grid;
- positive definiteness of the correlated-noise covariance matrix; and
- the stable Cholesky implementation.

Run the tests from the repository root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

A successful run executes three tests and ends with `OK`.

## Recommended first run

The program is configured through environment variables rather than command-line arguments. Its default model is `SEAM_3D`, which requires an external `seam.bin` file, and the default robust-analysis profile is computationally expensive.

Start with the built-in `Anomaly_2D` model and the smoke-test profile.

### Windows PowerShell

```powershell
$env:MODEL_TYPE = "Anomaly_2D"
$env:ROBUST_TWIN_TEST_MODE = "1"
$env:ROBUST_RECEIVER_COUNT = "6"
$env:RUN_MAIN_MODEL_ADVANTAGE_EVIDENCE = "0"
$env:RUN_FAST_PSDM = "0"
$env:MPLBACKEND = "Agg"
$env:OUTPUT_DIR = "output_images\anomaly_2d_smoke"
python .\Final_observation_system_adaptive_2D_3D_complete.py
```

### Linux or macOS

```bash
MODEL_TYPE=Anomaly_2D \
ROBUST_TWIN_TEST_MODE=1 \
ROBUST_RECEIVER_COUNT=6 \
RUN_MAIN_MODEL_ADVANTAGE_EVIDENCE=0 \
RUN_FAST_PSDM=0 \
MPLBACKEND=Agg \
OUTPUT_DIR=output_images/anomaly_2d_smoke \
python Final_observation_system_adaptive_2D_3D_complete.py
```

Results are written below `OUTPUT_DIR`. Even the smoke workflow is noticeably slower than the unit tests because it performs receiver design, independent velocity-split generation, localization comparisons, interval calibration, bootstrap analysis, and plotting.

## Model selection

Set `MODEL_TYPE` to one of the following values:

| Value | Dimensions | Velocity data | Grid shape |
|---|---:|---|---:|
| `Anomaly_2D` | 2D | Built into the program | `81 × 61` |
| `Anomaly_3D` | 3D | Built into the program | `41 × 41 × 31` |
| `Marmousi_2D` | 2D | External float32 binary file | `681 × 141` |
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
| `MODEL_TYPE` | `SEAM_3D` | Selects the velocity model |
| `OUTPUT_DIR` | `output_images` | Selects the output directory |
| `ADD_WELL_SENSORS` | `1` | Enables borehole candidate receivers |
| `ROBUST_COMPUTE_PROFILE` | `balanced` | Selects `smoke`, `quick`, `balanced`, or `production` |
| `ROBUST_TWIN_TEST_MODE` | `0` | Forces the smoke profile when set to `1` |
| `ROBUST_RECEIVER_COUNT` | Calculated internally | Sets the number of deployed receivers |
| `ROBUST_PARALLEL_WORKERS` | CPU-dependent | Sets the number of velocity-model worker processes |
| `RUN_MAIN_MODEL_ADVANTAGE_EVIDENCE` | `1` | Enables additional main-model evidence figures |
| `RUN_FAST_PSDM` | Inherits `RUN_DEVITO_RTM`; enabled by default | Enables the fast PSDM stage |
| `SAVE_MATLAB_TEXT_DATA` | `0` | Enables additional MATLAB/text output |

Fine-grained controls are defined in `reviewer_analysis_config()` and `robust_closed_loop_config()` in the main script.

## Standalone demonstration modes

The script provides two additional environment-controlled entry points.

### Robust advantage demonstration

```powershell
$env:ROBUST_ADVANTAGE_CASE_ONLY = "1"
$env:ADVANTAGE_CASE_FAST = "1"
python .\Final_observation_system_adaptive_2D_3D_complete.py
```

### Localization and migration evidence case

```powershell
$env:ROBUST_LOCALIZATION_MIGRATION_CASE_ONLY = "1"
$env:LOCALIZATION_MIGRATION_CASE_FAST = "1"
python .\Final_observation_system_adaptive_2D_3D_complete.py
```

These are still research computations and should not be confused with the quick unit tests.

## Code-analysis notes

- The source is a large, monolithic research script containing more than 300 top-level functions and 10 top-level classes. It is better treated as a reproducible experiment program than as a stable public Python API.
- Importing the module changes global Matplotlib settings and wraps `Figure.savefig`. Embedding it in another plotting application can therefore affect figures created elsewhere in the same process.
- Without `scikit-fmm`, travel-time calculation falls back to a homogeneous Euclidean-distance approximation based on the mean velocity. This permits execution but is not scientifically equivalent to the FMM result.
- An unrecognized `MODEL_TYPE` value falls through to the `Anomaly_2D` branch, so the spelling should be checked carefully.
- The default `balanced` profile contains many independent velocity realizations and events. Begin with `smoke` or `quick` on shared or resource-constrained machines.
- Velocity-arrival checkpoints can be reused between runs. Use a separate `OUTPUT_DIR` after changing physical or experimental parameters to avoid mixing incompatible results.
