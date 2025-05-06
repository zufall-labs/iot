# iot

🤖 Everything IoT in regards to Zufall Labs hardware products

```
/
├── .github/                      # GitHub specific configurations
│   ├── workflows/                # GitHub Actions CI/CD pipelines
│   ├── ISSUE_TEMPLATE/          # Issue templates
│   └── PULL_REQUEST_TEMPLATE/   # PR templates
│
├── hardware/                     # All hardware-related files
│   ├── mechanical/              # 3D designs and mechanical components
│   │   ├── cad/                 # CAD files (Fusion 360, SolidWorks, etc.)
│   │   ├── stl/                 # 3D printable files
│   │   └── drawings/            # Technical drawings and dimensions
│   │
│   ├── electronics/             # Electronic design files
│   │   ├── kicad/              # KiCad project files
│   │   │   ├── lib/            # Custom component libraries
│   │   │   ├── fp-lib-table    # Footprint library configurations
│   │   │   └── sym-lib-table   # Symbol library configurations
│   │   ├── datasheets/         # Component datasheets
│   │   └── production/         # Gerber files, BOM, assembly instructions
│   │
│   └── interfaces/             # Hardware interface specifications
│       ├── connectors/         # Connector pinouts and specifications
│       └── protocols/          # Communication protocol specifications
│
├── firmware/                    # Device firmware
│   ├── bootloader/             # Bootloader source code
│   ├── main/                   # Main firmware source code
│   ├── libs/                   # Shared firmware libraries
│   └── tools/                  # Firmware-specific tools
│
├── software/                   # Software components
│   ├── core/                   # Core business logic
│   ├── adapters/              # Hardware abstraction layers
│   │   ├── sensor-adapters/   # Different sensor implementations
│   │   └── comm-adapters/     # Communication protocol adapters
│   ├── api/                   # API definitions and implementations
│   ├── web/                   # Web applications
│   ├── mobile/                # Mobile applications
│   └── tools/                 # Development and debugging tools
│
├── tests/                      # Test suites
│   ├── hardware/              # Hardware test specifications
│   ├── firmware/              # Firmware test suites
│   └── software/              # Software test suites
│
├── docs/                       # Documentation
│   ├── architecture/          # System architecture documents
│   ├── hardware/              # Hardware documentation
│   ├── firmware/              # Firmware documentation
│   ├── software/              # Software documentation
│   ├── api/                   # API documentation
│   └── user/                  # End-user documentation
│
├── tools/                      # Development and build tools
│   ├── build-scripts/         # Build automation scripts
│   ├── ci-scripts/            # CI/CD helper scripts
│   └── dev-tools/             # Development utilities
│
├── config/                     # Configuration files
│   ├── dev/                   # Development environment configs
│   ├── prod/                  # Production environment configs
│   └── test/                  # Test environment configs
│
├── .gitignore                 # Git ignore rules
├── .editorconfig              # Editor configuration
├── LICENSE                    # Project license
├── README.md                  # Project overview and setup instructions
└── CONTRIBUTING.md            # Contribution guidelines
```
