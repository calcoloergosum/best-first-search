#!/usr/bin/env bash
GITROOT=$(dirname $0)/..
pytest -x --doctest-modules $GITROOT/src/best_first_search --cov=best_first_search
pytest -x -s $GITROOT/tests/ --cov=best_first_search --cov-append -m 'not visualize'
