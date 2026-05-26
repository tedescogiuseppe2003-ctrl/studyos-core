# StudyOS Core

StudyOS core is installed and synced from the core repository.

## Normal User Workflow

Step 1:
Open your existing course folder in VS Code.

Step 2:
Ask the agent:

> Install StudyOS in this folder using ~/Developer/studyos-core.

Step 3:
Answer the setup questions. The agent should ask only for missing essentials, then fill `subject.yaml` automatically.

Step 4:
Use the skills one by one:

- `study-os-import-sources`
- `study-os-inventory`
- `study-os-process-batch`
- `study-os-validate`
- `study-os-process-course`
- `study-os-synthesize`

## Install A New Subject

Run the installer from the core repo:

```sh
cd ~/Developer/studyos-core
python3 scripts/install_studyos.py ~/StudyOS-Test/TestCourse
```

The installer creates the subject folder structure, copies templates, copies course-local scripts into `study-os/scripts/`, and installs skills into `study-os/skills/`, `.agents/skills/`, and `.claude/skills/`.

`install_studyos.py` is core-only and is not copied into installed subject folders.

The installer also copies `STUDYOS_GUIDE.md` to the workspace root, copies `SKILLS_GUIDE.md` to `study-os/config/`, and initializes `study-os/state/studyos.sqlite`.

The installing agent should ask for subject name, raw source path, course level, course-material language, exam type, desired outputs, whether originals are read-only, and whether files should be copied into `inputs/`. It should then fill `subject.yaml`. StudyOS treats `raw_source.path` as read-only and imports approved files by copying them into `inputs/`.

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

Sync also updates `study-os/config/SKILLS_GUIDE.md`. If root `STUDYOS_GUIDE.md` exists, sync leaves it unchanged; if it is missing, sync copies the current guide template.

Sync does not touch raw course files or generated study work in `inputs/`, `outputs/`, `working/`, `review/`, `subject.yaml`, or `.git/`. It writes a sync log to `study-os/state/sync-log.md`.

Never run an old installed copy such as `study-os/scripts/install_studyos.py`. If one exists from an earlier install, `sync_studyos.py` removes it.
