# Tracework — development status

**Status: Development preview.** The public GitHub Pages workstation is an interface prototype and source-linked observation tool, **not a released standalone Tracework application**.

[Open the public preview](https://huntingthereferent.github.io/autobots-assemble/docs/live/work.html) · [Project scope](TRACEWORK.md) · [Viewer implementation notes](docs/live/README.md) · [Source repository](README.md)

## What the public preview currently represents

| Area | Current scope |
| --- | --- |
| Interface | An evolving browser-based workstation layout and navigation, hosted on GitHub Pages. |
| Execution observation | Read-only views of public GitHub Actions runs, jobs, revisions and available source-backed history; API and archival coverage can be incomplete. |
| Research records | Linked source records and evidence boundaries. A displayed finding is not independently proven by the page. |
| Runtime and local components | Source in this repository documents and implements bounded local processes. They are not automatically running inside the public web page. |
| Standalone Rust implementation | A separate implementation effort in development. The GitHub Pages preview does not establish its build, test or release status. |

**Presentation rule:** distinguish working source-backed features, interface prototypes, proposed capabilities and independently verified results. A passing CI job proves only the checks it executed.

## Development roadmap

This roadmap describes direction, **not promised features, deadlines or completed milestones**.

| Stage | Goal | Status |
| --- | --- | --- |
| Public preview | Explore interface design and inspect source-linked executions and research records. | Available; evolving |
| Rust implementation | Establish the standalone runtime and its executable contracts separately from GitHub Pages. | In development; build status not verified here |
| Integration | Connect the workstation interface to native execution and provenance records through explicit, tested interfaces. | Planned; not represented as complete |
| Distributable preview | Publish installation steps, reproducible checks, and a versioned artifact when they exist. | Not announced |

The roadmap may change as evidence, implementation and testing change. **A proposed feature should never be displayed as a live capability.**

## Development log

### 2026-10-24 — Public presentation clarified
- Labeled the GitHub Pages workstation a **Development Preview** and **interface prototype**.
- Distinguished the public viewer from the separate standalone Rust implementation.
- Added a documented status, development roadmap and release boundary for visitors.

For individual source changes and test outcomes, use the repository's [commit history](https://github.com/huntingthereferent/autobots-assemble/commits/main/) and [GitHub Actions runs](https://github.com/huntingthereferent/autobots-assemble/actions).

## Release notes

**Unreleased — no standalone Rust Tracework release is asserted by this page.**

Changes to the public preview are source updates, not evidence that a standalone executable has shipped. Release notes for a Rust build should begin when a versioned, reproducible build is available, with its own test results and known limitations.
