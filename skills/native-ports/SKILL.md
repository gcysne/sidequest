---
name: native-ports
description: Find, compare, install and maintain native PC ports of console games - decompilations, static recompilations and native-port runtimes (e.g. Ship of Harkinian, Zelda64Recomp, BanjoRecomp, PS4 ports). Use when the user wants to play or test such a project, or update one.
---

# Native ports, decompilations and recompilations

These projects are young, often Windows-only, frequently forked, and change fast.

## 1. Search before installing (every time)

1. Candidates: the repo the user named, its upstream and fork network (a fork's page says "forked from"), related
   projects for the same game, and general alternatives (the emulator for that console).
2. Compare activity and health via the GitHub pages/API: last commit on the active branch, latest release and date,
   recent issues, stars/forks, CI-built releases, Linux support.
3. Show a short comparison table with a recommendation; wait for the user's choice.
4. Read the chosen project's README and install docs in full: required game version, title ID, update, hashes.

## 2. Game files

The user supplies dumps/ROMs (AGENT.md). Verify them against the project's requirements (title ID, version,
hashes) and report mismatches instead of working around them.

## 3. Layout (one folder per project, never mixed)

```
<games folder>/
  dumps/<platform>/<TITLEID>-<version>/   user's files, read-only once verified
  ports/<platform>/<game-slug>/<owner>__<repo>/
    release-<tag>/  current -> release-<tag>     Steam and links point at current
    src/            git clone, if built from source
    user/           saves, configs, logs (native locations symlinked here)
    README.md       the user's pending steps, how to play, where things live, update/uninstall
    NOTES.md        source, tag/commit, sha256, build steps, Proton version, status, known issues
    uninstall.sh    removes links, menu entries, Steam shortcut; keeps saves unless --purge (archives them first)
  ports/_archive/   retired versions (kept until the user says delete)
```

Ask where the games folder lives (internal or SD card) the first time; record it in `notes/hardware.md` Observations.
Registry: one row per port in `notes/ports.md` (game, project, version, date, status works/partial/broken, path).

## 4. Install

- **Own the data paths:** find everywhere the program writes (read the source/launcher, then do a trial run and
  see what changed). Move it into `user/` and symlink the native locations to it. Back up any existing folder first.
- **Linux build available:** prefer it. Build inside a Distrobox container so build dependencies stay off the host;
  record the steps in NOTES.md.
- **Windows-only:** run through Proton as a non-Steam game with its own prefix; check the project's issues for
  Linux/Proton reports; note which Proton version worked.
- Vulkan requirements: `vulkaninfo --summary`.
- **Safety:** these are often unsigned binaries from small repos. Check whether releases come from CI or match a
  published hash, record the sha256, tell the user how established the project is; offer a source build for very new
  projects. Read install/update scripts before running them. Never run them with sudo.
- Steam: shortcut via the steam-library skill into a "Natives" collection with full artwork; native Linux builds get
  no compatibility tool; use a `launch.sh` wrapper when the program needs environment variables or the dump path.
- Tune (performance skill) and write `notes/games/<game>.md`. Log in `notes/CHANGELOG.md`.
- Never delete an older version or its saves without asking; back up saves before updating a port.
