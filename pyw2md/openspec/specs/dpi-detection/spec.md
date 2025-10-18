# dpi-detection Specification

## Purpose
TBD - created by archiving change add-dpi-scaling-support. Update Purpose after archive.
## Requirements
### Requirement: Platform-Aware DPI Detection
The application SHALL automatically detect system DPI settings across Windows, Linux, and macOS platforms.

#### Scenario: Windows DPI Detection
**Given** the application is running on Windows
**When** the application starts
**Then** it should detect the system DPI using Windows API
**And** calculate the scaling factor relative to 96 DPI
**And** return the correct scaling factor (e.g., 1.25 for 120 DPI, 1.5 for 144 DPI)

#### Scenario: Linux DPI Detection
**Given** the application is running on Linux
**When** the application starts
**Then** it should check GDK_SCALE environment variable
**And** fall back to tk scaling command if needed
**And** return the appropriate scaling factor

#### Scenario: macOS DPI Detection
**Given** the application is running on macOS
**When** the application starts
**Then** it should use tk scaling to detect Retina display scaling
**And** return the correct scaling factor (typically 2.0 for Retina)

### Requirement: DPI Awareness Setting
The application SHALL set appropriate DPI awareness level on supported platforms.

#### Scenario: Windows DPI Awareness
**Given** the application is starting on Windows
**When** DPI detection is initialized
**Then** it should call SetProcessDpiAwareness with PROCESS_PER_MONITOR_DPI_AWARE
**And** handle any errors gracefully without crashing

#### Scenario: Cross-Platform Compatibility
**Given** the application is running on any platform
**When** DPI awareness functions are called
**Then** non-supported platforms should gracefully skip DPI setting
**And** continue normal execution without errors

