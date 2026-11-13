# One-off repair scripts

These scripts were moved out of the project root because they perform specific edits to existing source files. They are not imported by Django, run during setup, or needed to start the application.

- `fix_education_links.py` applies a targeted Education-template link correction.
- `patch_education_application_view.py` replaces the Education application view with a particular older implementation.

Review the script and the current target file before running it. The patch script can overwrite newer work in `departments/education/views.py`; do not run it unless that exact replacement is intended. Both scripts locate the repository from their own file path and can be invoked from the project root:

```powershell
python scripts/one_off/fix_education_links.py
python scripts/one_off/patch_education_application_view.py
```
