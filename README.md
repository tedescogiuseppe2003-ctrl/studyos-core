# StudyOS Core

StudyOS core is installed and synced from the core repository.

## Normal installation UX

Before installation, the course folder may not have local StudyOS skills yet. The agent should install from the external StudyOS core repository, usually:

```sh
~/Developer/studyos-core
```

The user normally opens an existing course folder in VS Code and asks:

> Install StudyOS in this folder using ~/Developer/studyos-core.

The agent then uses the external core repo to run `scripts/install_studyos.py`, initializes or confirms the database, runs `scripts/sync_studyos.py` to sync latest scripts and skills, inspects the folder name and visible raw course files read-only, proposes a complete setup for `subject.yaml`, asks for approval or modifications, fills `subject.yaml` only after approval, creates or updates `STUDYOS_GUIDE.md`, and stops.

The agent should not ask setup questions one by one unless the proposed setup is impossible to infer.

The proposal should include:

- subject name
- course level
- language
- exam type
- desired outputs
- quality/depth mode
- visual handling depth
- formula handling depth
- validation depth
- `raw_source.path`
- read-only original files
- `copy_into_inputs` strategy

Then the agent asks:

> Do you approve this setup, or do you want modifications?

The user should not manually edit `subject.yaml` unless desired. The installing agent writes it from the approved proposal.

Installation and setup do not import files, run inventory, or process course material. After installation/setup, the user manually calls StudyOS skills step by step.

## Normal User Workflow

Step 1:
Open your existing course folder in VS Code.

Step 2:
Ask the agent:

> Install StudyOS in this folder using ~/Developer/studyos-core.

Step 3:
Review the proposed setup. Approve it or request modifications. The agent fills `subject.yaml` only after approval, creates or updates `STUDYOS_GUIDE.md`, and stops.

Step 4:
When ready, manually use the skills one by one:

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

After install, run sync from the same external core repo:

```sh
cd ~/Developer/studyos-core
python3 scripts/sync_studyos.py ~/StudyOS-Test/TestCourse
```

The installing agent should then inspect the folder name and visible raw course files read-only, infer reasonable defaults, and propose a complete setup including:

- Subject name
- Course level
- Course material language
- Exam type
- Original/raw course folder path
- Desired outputs
- Quality/depth mode: economy, standard, rigorous
- Visual handling depth: minimal, standard, rigorous
- Formula handling depth: normal, rigorous
- Validation depth: structural only, standard, rigorous audit
- Confirmation that original files are read-only
- Confirmation that StudyOS copies files into `inputs/`

For technical or formula-heavy subjects such as finance, risk management, statistics, econometrics, mathematics, derivatives, portfolio theory, and quantitative methods, the proposal should default to rigorous quality, visual, formula, and validation settings. Other courses should use standard defaults unless the folder contents suggest otherwise.

The agent should ask: "Do you approve this setup, or do you want modifications?" It should fill `subject.yaml` only after approval. StudyOS treats `raw_source.path` as read-only and imports approved files by copying them into `inputs/` only when the user later runs `study-os-import-sources`.

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

Sync does not touch raw course files or generated study work in `inputs/`, `outputs/`, `analysis/`, `review/`, `subject.yaml`, or `.git/`. It writes a sync log to `study-os/state/sync-log.md`.

Never run an old installed copy such as `study-os/scripts/install_studyos.py`. If one exists from an earlier install, `sync_studyos.py` removes it.

## Install Stops Before Course Work

During installation/setup, do not run:

- `study-os-import-sources`
- `study-os-inventory`
- `study-os-process-batch`
- `study-os-validate`
- `study-os-synthesize`
- any script that imports, inventories, summarizes, validates, or processes course material
