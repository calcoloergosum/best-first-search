#!/usr/bin/env bash
GITROOT=$(dirname $0)/..
PYTHONPATH=$GITROOT pytest -x --doctest-modules $GITROOT/best_first_search --cov=best_first_search
PYTHONPATH=$GITROOT pytest -x -s $GITROOT/tests/ --cov=best_first_search --cov-append -m 'not visualize'
