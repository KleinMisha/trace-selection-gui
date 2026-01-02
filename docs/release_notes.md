# Release Notes 

## :fontawesome-solid-tag: v1.0.0 ![Version](https://img.shields.io/badge/release-latest-purple)![Version](https://img.shields.io/badge/release-first-green)

- First working version of the GUI (:partying_face:)
- Features enabled by [`TimeTraceTools`](https://time-trace-tools-3ff349.gitlab.io/):
    - Opening experimental data from magnetic-tweezers experiments (both `.npz` and `.txt` formats supported)
    - Assigning labels to individual traces.
    - Assigning labels to selected time-widows (referred to as sections) of a trace. 
- Exporting labels to files, such that these can be read in by [`TimeTraceTools`](https://time-trace-tools-3ff349.gitlab.io/). 
- GitLab CI/CD actions when pushing to the main branch: 
    - Runs unit tests (SUCCESS REQUIRED TO TRIGGER NEXT ACTION)
    - Builds and deploys this website ([MkDocs](https://squidfunk.github.io/mkdocs-material/)) (SUCCESS REQUIRED TO TRIGGER NEXT ACTION)
    - Optional version bump (both in `pyproject.toml` and as a :material-git: tag) (MANUAL TRIGGER)
