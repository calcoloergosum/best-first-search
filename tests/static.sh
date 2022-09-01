GITROOT=$(dirname $0)/..
pylint $GITROOT/best_first_search $GITROOT/setup.py
mypy $GITROOT/best_first_search
