import os

# Read environment variables
github_username = os.getenv("GITHUB_USERNAME")
github_token = os.getenv("GITHUB_TOKEN")

# Your project's configuration template
content = f"""
[project]
name = ""
version = ""
description = ""
authors = [
    {{name = "Hansotto Kristiansen", email = "hansotto.kristiansen@gmail.com"}},
]
dependencies = [
    "firebase-admin>=6.4.0",
    "Flask==2.3.2",
    "Flask-Cors==4.0.0",
    "pandas==2.1.1",
    "PyJWT==2.8.0",
    "python-dateutil==2.8.2",
    "requests==2.31.0",
    "waitress==2.1.2",
    "seaborn>=0.13.0",
    "Core @ git+https://{github_username}:{github_token}@github.com/{github_username}/core.git@main",
]


requires-python = ">=3.10,<3.13"
readme = "README.md"
license = {{text = "Proprietary"}}


[tool.pdm.dev-dependencies]
test = [
    "pytest>=7.4.3",
]
lint = [
    "black>=23.10.1",
]
"""

# Write the generated config to pyproject.toml
with open("pyproject.toml", "w") as f:
    f.write(content)
