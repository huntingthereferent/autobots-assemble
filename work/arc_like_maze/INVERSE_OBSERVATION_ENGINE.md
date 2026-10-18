# A/B inverse observation — original F3 mathematics

This is independent A/B mathematical work, not another REA experiment, another
chatbot, or a new definition of the Language Referent. The source of truth is
the existing work/arc_like_maze/math.py World.step, World.apply, and nine
candidate laws with phi=(0,a,b) for a,b in F3.

Given an explicitly admitted FULL mathematical endpoint for a rooted action
word, the engine retains exactly the candidate laws whose original source
transitions predict that endpoint. It does not coerce an ARC visible frame into
an F3 state or invent an observation. An exact conflict returns CONTRADICTION.
An insufficient search budget returns OBSERVATION_WALL.

## The actual mathematical operation

From the currently surviving worlds, enumerate bounded words in generators
A,B, compute the endpoint of each word by World.apply, partition worlds by the
outcome, and choose the word minimizing the largest possible surviving group.
Break ties by maximizing separated candidate pairs, then shortest length and
lexical word order. Return the set of POSSIBLE outcomes without pretending any
of them has been observed. A new independently admitted observation can enter
the same calculation again.

## New finite result and its lower bound

With the original F3 law:

    A(x0,x1,x2) = (x0+1,x1,x2)
    B(x0,x1,x2) = (x0,x1+x0+1,x2+phi[x1])
    phi = (0,a,b)

All arithmetic is modulo three. The first two coordinates of every rooted
word are independent of a,b, while the final coordinate has only three
possible values. A single full-state rooted observation therefore cannot
distinguish all nine candidate laws. Two are necessary.

The two particular rooted words BB and BBB are sufficient:

    BB  -> (0,2,a)
    BBB -> (0,0,a+b)

Thus a = z(BB), and b = z(BBB) - z(BB) modulo 3. This is an algebraic
certificate within the original nine-law family, checked by executing
World.apply on every candidate. The program chooses a next word from predicted
outcome partitions; it need not hard-code the two-word certificate as a script.

## Execute the actual source computation

    python -m unittest network.tests.test_arc_like_inverse_observation_engine -v
    python -m work.arc_like_maze.inverse_observation_engine --certificate
    python -m work.arc_like_maze.inverse_observation_engine --demo-phi 1,2 --certificate
    python -m work.arc_like_maze.inverse_observation_engine --observe BB=0,2,1

The demo uses a DECLARED SYNTHETIC F3 World, not a live ARC environment.
Neither an A/B universal theorem, real hidden ARC state mapping, nor a solved
native game follows. Other already-built mathematical families (including
Engine 1 and the 48-law window systems) have their own proof conditions.

No imports, submodules, source editions, or dependencies from REA are used.
