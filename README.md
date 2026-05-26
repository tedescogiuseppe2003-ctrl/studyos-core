# StudyOS Core

StudyOS core is installed and synced from the core repository.

## Install A New Subject

Run the installer from the core repo:

```sh
cd ~/Developer/studyos-core
python3 scripts/install_studyos.py ~/StudyOS-Test/TestCourse
```

The installer creates the subject folder structure, copies templates, copies course-local scripts into `study-os/scripts/`, and installs skills into `study-os/skills/`, `.agents/skills/`, and `.claude/skills/`.

`install_studyos.py` is core-only and is not copied into installed subject folders.

## Sync An Existing Subject

Run sync from the core repo:

```sh
cd ~/Developer/studyos-core
python3 scripts/sync_studyos.py ~/StudyOS-Test/TestCourse
```

Sync updates course-local scripts in `study-os/scripts/` and replaces installed skills in:

- `study-os/skills/`
- `.agents/skills/`
- `.claude/skills/`

Sync does not touch raw course files or generated study work in `inputs/`, `outputs/`, `working/`, `review/`, `subject.yaml`, `study-os/state/`, or `.git/`.

Never run an old installed copy such as `study-os/scripts/install_studyos.py`. If one exists from an earlier install, `sync_studyos.py` removes it.
