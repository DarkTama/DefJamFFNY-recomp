# Domain Model: Def Jam: Fight for NY Recomp

## Glossary

### Fighter Profile
The persistent state and configuration of a created fighter, including physical appearance, stats, fighting styles, moveset, and story progression.

### Vitals
The basic physical measurements of a fighter (height, weight, and body type) chosen during character creation.

### Body Type
The categorical frame size of a fighter (e.g. Medium, Large, Extra Large) that governs skeleton scaling and silhouette.

### Fighter Model
The 3D geometry and texture assets that represent a combatant in the ring and in cutscenes.

### Part Descriptor
A structured reference defining an individual aesthetic component of a fighter (such as head shape, hairstyle, facial hair, upper body clothing, lower body clothing, shoes, or accessories).

### Sketch Artist
The interactive character creation sequence in Story Mode, presented as a police detective's forensic sketchpad.

### Unit System
The convention of measurement used to present fighter vitals: Imperial (feet/inches, pounds) or Metric (centimeters, kilograms).

### Save Signature
The 3-tier cryptographic authentication system embedded within a save file to validate integrity:
- Seal 1 (`0x10..0x23`): HMAC-SHA1 of metadata block (`0x4C..0x8B`).
- Seal 2 (`0x24..0x37`): HMAC-SHA1 of fighter profile (`0x8C..end`).
- Seal 3 (`0x38..0x4B`): Master Seal over header (`0x00..0x37`), signing Seal 1 and Seal 2 together.

### Career Progression
Story Mode economy and stats stored inside the fighter profile:
- Cash (`0x00A0` and `0x01E8`): Currency used in shops (clothing, jewelry, tattoos, movesets).
- Dev Points (`0x00A8`): Points used at the Gym to increase combat attributes.

### Asset Override
A file system redirection that substitutes loose user-supplied content in place of archived game dump files without modifying original disc data.
