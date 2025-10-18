# font-scaling Specification

## Purpose
TBD - created by archiving change add-dpi-scaling-support. Update Purpose after archive.
## Requirements
### Requirement: Dynamic Font Scaling
All application fonts SHALL scale proportionally based on the detected DPI scaling factor.

#### Scenario: Base Font Scaling
**Given** the base UI font is defined as ("Segoe UI", 9)
**And** the system scaling factor is 1.5
**When** the application initializes fonts
**Then** the scaled font should be ("Segoe UI", 14) [9 * 1.5 rounded]

#### Scenario: Code Font Scaling
**Given** the base monospace font is defined as ("Cascadia Code", 9)
**And** the system scaling factor is 2.0
**When** the application initializes fonts
**Then** the scaled font should be ("Cascadia Code", 18)

#### Scenario: Title Font Scaling
**Given** the base title font is defined as ("Segoe UI Semibold", 10)
**And** the system scaling factor is 1.25
**When** the application initializes fonts
**Then** the scaled font should be ("Segoe UI Semibold", 13) [10 * 1.25 rounded]

### Requirement: Font Size Limits
Font scaling SHALL respect minimum and maximum size limits to maintain readability.

#### Scenario: Minimum Font Size Enforcement
**Given** the minimum font size is configured as 8
**And** the calculated scaled size is 6
**When** font scaling is applied
**Then** the font size should be clamped to 8

#### Scenario: Maximum Font Size Enforcement
**Given** the maximum font size is configured as 24
**And** the calculated scaled size is 30
**When** font scaling is applied
**Then** the font size should be clamped to 24

### Requirement: UI Element Scaling
UI components SHALL scale proportionally with fonts to maintain visual consistency.

#### Scenario: Button Height Scaling
**Given** a button has base height of 30 pixels
**And** the scaling factor is 1.5
**When** the UI is rendered
**Then** the button height should be 45 pixels

#### Scenario: Spacing Scaling
**Given** a layout has base spacing of 10 pixels
**And** the scaling factor is 2.0
**When** the UI is rendered
**Then** the spacing should be 20 pixels

#### Scenario: Icon Size Scaling
**Given** an icon has base size of 16x16 pixels
**And** the scaling factor is 1.75
**When** the UI is rendered
**Then** the icon should be scaled to 28x28 pixels [16 * 1.75 rounded]

