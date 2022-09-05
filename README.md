# Best first search, using pre-sorted iterators

![build](https://github.com/studentofkyoto/best-first-search/actions/workflows/push.yml/badge.svg)
[![codecov](https://codecov.io/gh/studentofkyoto/best-first-search/branch/main/graph/badge.svg?token=VCRNMAFGFB)](https://codecov.io/gh/studentofkyoto/best-first-search)

![sample_astar](assets/sample_astar.gif)

It finds the minimum cost path on a graph, where the cost of a path is linear sum of each edge's weight in it. To call the function, the followings are required:

- termination condition
- neighbor iterator; pre sorting the iterator helps the performance so that it iterates through each neighbor in ascending order of cost.
- cost addition function; in case you want to inject relaxation

For usage, take a look at `best_first_search.example`.
