# qpinvest

## Installation Instructions

To install Core from azure feed, follow these steps:

1. Add the file `pdm.toml` to the project root.

```toml
[tool.pdm.source]
name = "azure"
url = "<feed-url>"
username = "<username>"
password = "<PAT>"
