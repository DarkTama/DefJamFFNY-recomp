# ADR 0001: Character Creation Enhancements, Standalone Editor, and Asset Overrides

## Status
Accepted

## Context
In *Def Jam: Fight for NY*, character creation (the Sketch Artist interface) is strictly embedded in the start of Story Mode. Players are restricted to Imperial measurements (feet/inches, pounds) and male protagonists. Furthermore, character appearance data is locked inside binary Xbox save files protected by an HMAC-SHA1 signature.

We want to support:
1. Metric system measurements (centimeters and kilograms) for character creation vitals.
2. An external character creator / importer that allows building fighters without starting Story Mode from scratch.
3. Access to female character models for created fighters.
4. Custom 3D model injection.

All changes must strictly respect project hygiene: no game dump data or proprietary binary meshes may be committed to Git.

## Decision

1. **Metric Display via In-Engine PAL Logic Interception**:
   Reverse-engineering revealed that the game's Flash UI (`screens/story/Sketch.big`) contains built-in metric conversion routines (`footConvert` and `weightConvert`) that activate when `g_language == "french"` (Language ID 3). We will intercept the native Flash callback `Game.GetLanguage()` (`sub_00046CB0` in `src/recomp_manual.c`) when `[gameplay] units = metric` is configured in `settings.ini`, returning Language ID 3 while keeping menu text in English.

2. **Standalone CAW Editor & Exporter Tool**:
   Develop a standalone Python application using `tkinter` in `tools/caw-editor/`. The editor manipulates human-readable JSON character presets and compiles/signs valid binary Xbox profile files (`20CM` / `MC02` format) using RFC 2104 HMAC-SHA1 with the title's signature key. The tool places generated files directly into `save/UserData/45410049/<hash>/`.

3. **Female Fighter Support**:
   The engine already contains female skeletons, animation sets, and character models (`V2IP_400A` through `V2IP_405A`). The standalone editor will permit selecting female model indices for any created fighter profile. Players using female models in Story Mode will experience the original authored male voice and cutscene dialogue.

4. **Loose-File Asset Redirection for 3D Models**:
   Rather than repacking `.viv` archives, a file-IO hook in `src/hooks/` will check for loose replacement `.o` and `.xsh` files in a local, gitignored `mods/characters/` folder. If a loose file exists, file operations are redirected to it transparently.

## Consequences

### Positive
- Metric units render using authentic game fonts without patching precompiled SWF bytecode.
- Unlimited character presets can be created, shared, and backed up as plain JSON files.
- Female models become fully playable across Exhibition and Story modes without altering original game assets.
- Modders can test new models by dropping files into `mods/characters/` without altering their game dump.
- Complies 100% with repository publication and copyright policies: zero proprietary assets in version control.

### Trade-offs / Limitations
- Playing as female in Story Mode produces mismatched pronouns and voice lines in pre-rendered scenes.
- Custom models must be pre-rigged to the Xbox skeleton and export to the native `.o` container format.
