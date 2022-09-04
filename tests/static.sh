#!/usr/bin/env bash
GITROOT=$(dirname $0)/..
isort -c -diff $GITROOT/src/best_first_search
pylint $GITROOT/src/best_first_search $GITROOT/setup.py
mypy $GITROOT/src/best_first_search
