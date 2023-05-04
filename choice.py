from functools import reduce
import random


class Choice:

    @classmethod
    def solo(cls, outcome):
        return cls([(outcome, 1)])

    @classmethod
    def delayed(cls, func):
        def _delayed(*args, **kwargs):
            return Choice.solo(_Delayed(func, *args, **kwargs))
        return _delayed

    @classmethod
    def of(cls, *args):
        return cls.flat(args)

    @classmethod
    def flat(cls, args):
        iter_args = iter(args)
        first = next(iter_args)
        if not isinstance(first, cls):
            first = cls.solo(first)
        outcome = reduce(cls.either, iter_args, first)
        return outcome

    @classmethod
    def weighted(cls, weight, outcome):
        return cls([(outcome, weight)])

    @classmethod
    def percentage(cls, percent, outcome):
        return cls([(outcome, percent)], total=100)

    @classmethod
    def otherwise(cls, outcome, total=None):
        return cls([(outcome, None)], total=total, is_remainder=True)

    @classmethod
    def either(cls, a, b):
        # If the arguments aren't of this type, convert them
        if not isinstance(a, cls):
            a = cls.solo(a)
        if not isinstance(b, cls):
            b = cls.solo(b)

        # If neither are constrained, just add them
        if a.total is None and b.total is None:
            # The only issue is if we want to add a remainder, we need to have a total
            if a.is_remainder or b.is_remainder:
                raise ValueError(
                    "Cannot join remainders without any declared total."
                )
            return cls(a.outcomes + b.outcomes)

        # If the left argument is a remainder, that is also invalid
        if a.is_remainder:
            raise ValueError(
                "Remainders may only occur at the end of a disjunction"
            )

        # Check that the totals do not invalidate this disjunction
        if a.total is not None and a.summed == a.total:
            raise ValueError(f"Cannot join a to b as a is normalized.")
        if b.total is not None and b.summed == b.total:
            raise ValueError(f"Cannot join a to b as b is normalized.")
        if a.total is not None and b.total is not None and a.total != b.total:
            raise ValueError(
                f"Cannot join a to b as they have different expected "
                f"normalizations: {a.total=} vs {b.total=}"
            )

        # The total is either the same or determined by one of them
        total = a.total or b.total
        remaining = total - (a.summed + b.summed)
        if remaining < 0:
            raise ValueError(
                f"Cannot join a to b as joining them would exceed "
                f"their allowed total by {-remaining}"
            )

        # If b is a remainder, hydrate its outcome weight
        if b.is_remainder:
            (b_outcome, _) = b.outcomes[0]
            return cls(a.outcomes + [(b_outcome, remaining)], total=total)
        else:
            return cls(a.outcomes + b.outcomes, total=total)

    def __init__(self, outcomes, total=None, is_remainder=False):
        self.is_remainder = is_remainder
        if is_remainder and len(outcomes) != 1:
            raise ValueError("Remainders cannot present multiple outcomes")
        self.outcomes = outcomes
        self.summed = sum(v for (_, v) in outcomes if v is not None)
        if total is not None:
            if self.summed > total:
                raise ValueError(f"Outcomes sum to {self.summed} instead of {total}")
        self.total = total

    def __or__(self, other):
        return self.either(self, other)

    def __repr__(self):
        clsname = self.__class__.__name__
        if self.is_remainder:
            if self.total is None:
                return f"{clsname}.otherwise({self.outcomes[0][0]})"
            else:
                return f"{clsname}.otherwise({self.outcomes[0][0]}, total={self.total})"

        elif self.total is None:
            body = ", ".join(
                f"{clsname}.weighted({weight}, {outcome})"
                for (outcome, weight) in self.outcomes
            ) 
            return f"{clsname}.of({body})"

        else:
            total = self.total
            body = ", ".join(
                f"{clsname}.weighted({weight/total}, {outcome})"
                for (outcome, weight) in self.outcomes
            )
            return f"{clsname}.of({body})"

    @classmethod
    def _evaluate(cls, rng, data):
        if isinstance(data, cls):
            total = data.total or data.summed
            maximums = []
            last = 0
            for (item, weight) in data.outcomes:
                maximums.append((last, item))
                last += weight

            pick = rng.uniform(0, total)
            found = next(item for (x, item) in reversed(maximums) if pick >= x)
            return cls._evaluate(rng, found)

        elif isinstance(data, (tuple, list)):
            return type(data)([cls._evaluate(rng, d) for d in data])

        elif isinstance(data, dict):
            return type(data)({k: cls._evaluate(rng, v) for (k, v) in data.items()})

        elif isinstance(data, _Delayed):
            args = [cls._evaluate(rng, arg) for arg in data.args]
            kwargs = {k: cls._evaluate(rng, v) for (k, v) in data.kwargs}
            return cls._evaluate(rng, data.func(*args, **kwargs))

        else:
            return data

    def evaluate(self, rng=None):
        rng = rng or random.Random()
        return self._evaluate(rng, self)


class _Delayed:

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        args = ", ".join(
            [f"{arg}" for arg in self.args] +
            [f"{key}={value}" for (key, value) in self.kwargs.items()]
        )
        return f"{self.func.__name__}({args})"
