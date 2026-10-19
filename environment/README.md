# Environments

## Public analysis and review

Use Python 3.11 (validated with 3.11.17; also tested independently on 3.12.14) and `pip install -e ".[review]"`.
Direct requirements are exact in pyproject.toml; `review-constraints.txt` records
the validated transitive versions. To use these constraints in a fresh environment:

```text
python -m pip install -c environment/review-constraints.txt -e ".[review]"
python -m pip check
```

The analysis environment uses NumPy 2.4.6, SciPy 1.17.1 and trimesh 4.9.0.
Matplotlib is needed only for aggregate figures. The public tests and aggregate
commands run without torch, MHR, clad-body, participant data or downloaded models.
Optional torch tests have also been run separately with PyTorch 2.8.0 on an
invented differentiable model; this is not validation of a real native fit.

## Historical native runtime

The saved E2-1 native record identifies Python 3.12.12, Linux x86_64 (WSL2 kernel
6.6.114.1, glibc 2.39), torch 2.8.0, NumPy 2.3.5, SciPy 1.18.1 and pymomentum 0.1.0,
with CPU execution and no CUDA runtime. `native-observed.json` preserves those
observations without personal paths. It is an observed environment record, not a
portable dependency lock. This distinct historical environment has not been
recreated by the public installer. In particular, the base package's analysis
NumPy/SciPy pins are not a claim about the historical native versions.

The `native` extra adds torch 2.8.0 and h5py 3.15.1 for optional component tests
and D-FAUST input reading; it does not install MHR, pymomentum, model assets or
the exact historical native runtime. For actual native use, separately provision
the official MHR revision and its upstream runtime, compare observed versions and
verify code/assets against `configs/model_hashes.json`. Never silently substitute
a newer model. Source fitting resource guards require Linux. The native loader
uses CPU, one torch thread and the requested frozen seed.

## Optional historical waist comparator

clad-body is pinned by revision and every consumed Python-file hash. Its upstream
packaging requires Python >=3.12 and a newer trimesh version, while the historical
comparison imported its source into the recorded Python 3.11 / trimesh 4.9.0
analysis environment. These requirements are inconsistent; silently upgrading
trimesh would change the frozen comparison environment.

A separate compatibility check installed the exact upstream distribution without
its dependency solver and confirmed all pinned source bytes plus the 61%-height
convex-hull measurement on an invented prism. The following explicit exception
was tested in a disposable comparator environment:

```text
python -m pip install --no-deps --ignore-requires-python https://github.com/datar-psa/clad-body/archive/a2140a74555a6382e1712ec1a5d8dc939b59e655.zip
python -m pytest tests/test_release_integration.py -k pinned_official_comparator
```

This environment intentionally does not satisfy that distribution's declared
Python/trimesh requirements. Keep it separate from the clean Level 1 environment;
it is a bounded source-compatibility check, not a general support claim. No
comparator dependency or model is downloaded automatically by the test suite.
