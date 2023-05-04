import random

from choice import Choice


pct = Choice.percentage
weight = Choice.weighted
otherwise = Choice.otherwise
delayed = Choice.delayed


_join = delayed(lambda *s: "".join(s))
_a = delayed(lambda x: f"an {x}" if any(x.startswith(v) for v in "aeiou") else f"a {x}")
_cap = delayed(lambda x: x.title())


def some_story(rng):
    name = Choice.of("Cheri","Fox","Morgana","Jedoo","Brick","Shadow","Krox","Urga","Zelph")
    pronouns = Choice.of(
        {"their": "their", "they": "they"},
        {"their": "his", "they": "he"},
        {"their": "her", "they": "she"},
    )
    monster = Choice.of(
        "dragon","ogre","witch","wizard","goblin","golem","giant","sphinx","warlord",
        "oubliette","archeopteryx","iguana man",
    )
    occupation = Choice.of("baker", "warrior")
    stuff = {
        "baker": Choice.of("baked bread", "decorated cupcakes", "folded dough", "made croissants", "iced a cake"),
        "warrior": Choice.of(
            _join("fought ", _a(monster)),
            _join("saved a village from ", _a(monster)),
            _join("battled ", _a(monster)),
            _join("defeated ", _a(monster)),
        ),
    }

    hero = name.evaluate(rng)
    heroPronouns = pronouns.evaluate(rng)
    heroOccupation = occupation.evaluate(rng)
    didstuff = stuff[heroOccupation]

    story = Choice.solo(
        _join(
            _cap(hero), " was a great ", heroOccupation, " and this song tells of ", heroPronouns["their"],
            " adventure.  ", _cap(hero), " ", didstuff, ", then ", heroPronouns["they"], " ", didstuff, ", then ", heroPronouns["they"], " went home to read a book."
        )
    )

    return story.evaluate(rng)
