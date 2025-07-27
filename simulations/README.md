# Simulations Directory

This directory stores persistent simulation data for the AnyLogic MCP Server.

## Structure

- `results/` - Individual simulation run data
  - `sim_YYYYMMDD_HHMMSS/` - Each simulation gets its own directory
    - `metadata.json` - Simulation parameters and status
    - `outputs.json` - Simulation results and outputs
    - `raw_results.json` - Raw AnyLogic output data
- `exports/` - Exported data in various formats
  - `csv/` - CSV exports for analysis
  - `json/` - JSON exports for programmatic access
  - `reports/` - Generated reports and summaries

## Data Retention

- Simulation results are kept indefinitely
- Use cleanup tools to archive or remove old results
- Directory names include timestamps for easy sorting