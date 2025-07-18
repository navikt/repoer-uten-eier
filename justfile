# https://just.systems

set shell := ["zsh", "-c"]

default:
    just --list --unsorted

# Henter data
fetch: bootstrap
    ./fetch_data.py

# Analyserer data
analyze: bootstrap
    for i in {1..700..20}; do ./analyze.py --num-authors $i; done

# Sletter data
clean: bootstrap
    rm -rf data

# Linter kode
lint: bootstrap
    uvx ruff check .

# Formaterer kode
format: bootstrap
    uvx ruff format .

# Installerer avhengigheter
bootstrap:
    uv --version || brew install uv
    uvx --version || brew install uvx
