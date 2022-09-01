#!/usr/bin/env bash
GITROOT=$(dirname $0)/..
isort -c -diff $GITROOT/best_first_search
pylint $GITROOT/best_first_search $GITROOT/setup.py
mypy $GITROOT/best_first_search
