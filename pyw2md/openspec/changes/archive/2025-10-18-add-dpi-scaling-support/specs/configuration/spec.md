# DPI Scaling Configuration Specification

## ADDED Requirements

### Requirement: Automatic DPI Detection Configuration
Users SHALL be able to enable or disable automatic DPI detection.

#### Scenario: Enable Auto-Detection by Default
**Given** a fresh installation of the application
**When** the application first starts
**Then** automatic DPI detection should be enabled by default
**And** the UI should scale according to system DPI

#### Scenario: Disable Auto-Detection
**Given** the user has disabled automatic DPI detection in settings
**When** the application restarts
**Then** DPI detection should be skipped
**And** the scaling factor should use the manual value

### Requirement: Manual Scaling Factor Override
Users SHALL be able to manually set a custom scaling factor.

#### Scenario: Set Custom Scaling Factor
**Given** the user sets a manual scaling factor of 1.75
**And** automatic detection is disabled
**When** the application applies scaling
**Then** all UI elements should scale by 1.75x
**And** fonts should increase proportionally

#### Scenario: Reset to Default
**Given** the user has set a custom scaling factor
**When** the user resets to default settings
**Then** the scaling factor should return to 1.0
**And** automatic detection should be re-enabled

### Requirement: Configuration Persistence
DPI scaling settings SHALL be saved and restored between application sessions.

#### Scenario: Save DPI Settings
**Given** the user has configured custom DPI settings
**When** the application closes
**Then** the settings should be saved to config.json
**Including** auto_detect flag, scaling_factor, and font size limits

#### Scenario: Restore DPI Settings
**Given** DPI settings were previously saved
**When** the application starts
**Then** the saved settings should be loaded from config.json
**And** applied before any UI is created

### Requirement: Font Size Configuration
Users SHALL be able to configure minimum and maximum font sizes.

#### Scenario: Set Font Size Limits
**Given** the user sets minimum font size to 10 and maximum to 20
**When** DPI scaling is applied
**Then** no font should be smaller than 10pt
**And** no font should be larger than 20pt

#### Scenario: Disable Font Size Limits
**Given** the user disables font size limits
**When** DPI scaling is applied
**Then** fonts should scale without restrictions
**And** very large or very small fonts may appear