Choice
======

Randomly generate data based on probabilistic rules.

```
from choice import Choice

(Choice.weighted("first", 1) | Choice.weighted("double", 2)).evaluate()
```
