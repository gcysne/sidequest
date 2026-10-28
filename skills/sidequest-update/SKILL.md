---
name: sidequest-update
description: Update Sidequest itself (scripts, agent, skills, device knowledge, Decky plugin) to a newer release, after the user agrees. Use when the session-start check reports a new version or the user asks to update Sidequest.
---

# Update Sidequest

The session-start hook (`sidequest-update-check`, at most once a day) compares the installed version
(`~/.local/lib/sidequest/VERSION`) with the latest GitHub release and tells you when there's a newer one.

1. Tell the user the new version and the highlights from its release notes / `CHANGELOG.md`; ask whether to update.
   Never update without a yes. Mention it needs Desktop Mode (the plugin copy uses sudo) and restarts Decky.
2. In the clone (`SIDEQUEST_SRC` in `~/.config/sidequest/config`): `git status` must be clean (if the user has local
   changes or an open contribution branch, ask first), then `git fetch --tags origin` and check out the release tag
   (`git checkout v<version>`) or `git pull --ff-only` on `main`.
3. Run `./install.sh` from the clone (it keeps settings, the notebook and `CLAUDE.local.md`; it updates the agent,
   skills, knowledge folders and the plugin).
4. Session changes (agent instructions, skills) apply to the **next** session: offer to restart it
   (Quick Access > Sidequest > New conversation, or `claude-session --restart`).
5. Log the update in `notes/CHANGELOG.md` (old → new version).
