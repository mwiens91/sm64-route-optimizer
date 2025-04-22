# Super Mario 64 Route Optimizer

This program generates optimal Super Mario 64 70 star routes. The
intended audience is the nearly non-existent niche of players who are
serious enough to want to get the most out of their 70 star times, but
not serious enough to learn proper speedrunning techniques and an actual
[70 star RTA route](https://ukikipedia.net/wiki/RTA_Guide/70_Star).

To use the program, you provide times for stars in a configuration file,
run a script, and it'll generate an optimal route along with a webpage
to display it.

The optimization algorithm takes into account

- prerequisite relationships (e.g., we need the wing cap to get the
  "Shoot to the Island in the Sky" star on Bob-omb Battlefield)
- mutual exclusivity relationships introduced by combining 100 coin
  stars with regular course stars (e.g., if we have separate times for
  collecting 8 red coins and for collecting both 8 red coins and the 100 coin
  star at once on Whomp's Fortress, we can only include one of those
  times in the route)
- star count requirements (e.g., we need at least 8 lobby stars to access
  Bowser in the Dark World and any stars outside the lobby)
- required stars, of which there is only one—the Dire, Dire Docks "Board
  Bowser’s Sub" star, which is required to access Bowser in the Fire
  Sea and complete the game

Note that the algorithm does not take into account travel time between
courses (see [Advice](#advice) for helpful workarounds).

## Setup

The program uses the Python libraries
[Cerberus](https://docs.python-cerberus.org/) for data validation and
[FastHTML](https://fastht.ml/) for HTML generation. Preferably from
within a virtual environment, you can install these libraries with

```bash
pip install cerberus python-fasthtml
```

or from the [requirements file](requirements.txt) with

```bash
pip install -r requirements.txt
```

## Usage

To run the route optimizer execute the
[`sm64-route-optimizer.py`](sm64-route-optimizer.py) script with

```bash
./sm64-route-optimizer.py
```

Running this command will fail without a user configuration file (see
[Configuration](#configuration)). However, we can still run the
optimizer without a user configuration file with the
`--generate-fake-times` flag (this uses information from the
[example configuration file](config.toml.example) as a fallback when no
user configuration file is found):

```bash
./sm64-route-optimizer.py --generate-fake-times
```

Successfully executing either of these commands will generate an HTML
file `index.html` at the root of the repository displaying an optimal 70
star route!

### Excluding stars and courses

We can exclude specific courses from the route with the
`--exclude-course-ids` flag. For example, to exclude stars from Bob-omb
Battlefield and Rainbow Ride, you'd run

```bash
./sm64-route-optimizer.py --exclude-course-ids BOB RR
```

Similarly, we can also exclude specific stars from the route with the
`--exclude-star-ids` flag. For example, to exclude Bob-omb Battlefield's
second star "Footrace with Koopa the Quick" and Cool, Cool Mountain's
third star  "Big Penguin Race", you'd run

```bash
./sm64-route-optimizer.py --exclude-star-ids BOB2 CCM3
```

Course IDs are acronyms of course names and star IDs follow a naming
convention detailed in [Configuration](#configuration).

### Limiting upper level stars

We can limit the number of stars obtained from the castle's upper levels
with the `--max-upper-level-stars` flag. For example, to ensure that you
obtain at least 51 stars from areas outside the castle's upper levels,
you'd run

```bash
./sm64-route-optimizer.py --max-upper-level-stars 19
```

This can be useful for ensuring the second MIPS star is available before
entering upstairs (see [MIPS is a menace](#mips-is-a-menace)).

### Getting help

To see all options along with descriptions, run

```bash
./sm64-route-optimizer.py -h
```

## Output

After finding an optimal route, the program generates an HTML file
`index.html` at the root of the repository. An example is shown
[here](https://mwiens91.github.io/sm64-route-optimizer/). The page first
displays a route summary, which includes the following information:

- the sum of star times for the route. This will shorter than the actual
  route time, since travel time is not factored into the sum
- the number of stars obtained from each castle location:
  - lobby: the first floor including Bob-omb Battlefield, Bowser in the
    Dark World, etc.
  - courtyard: the courtyard area with Big Boo's Haunt
  - basement: the basement including Lethal Lava Land, Bowser in the
    Fire Sea, etc., and the vanish cap stage under the moat
  - upstairs: the second floor including Snowman's Land, Wet-Dry World,
    etc.
  - tippy: the third floor (the "tip" of the castle) including Tick Tock
    Clock, the "Wing Mario Over the Rainbow" castle star stage, etc.

Following the summary is a grid of tables—one for each course where the
user has recorded at least one star time.[^castle-is-a-course] Each
table row contains information for every star with an entered time:

- a check mark (✓) indicating whether the star is included in the route
- the star number from its course's star menu[^star-number-special-cases]
- the star name
- the average time required to obtain the star

Above each table, the total number of stars obtained from that course is
displayed

[^castle-is-a-course]: For simplicity, castle stars—such as "The
  Princess’s Secret Slide", "MIPS Bunny Chase", "Tower of the Wing
  Cap"—are gruoped under a "course" titled "Peach’s Castle Secret Stars".
[^star-number-special-cases]: Regular course stars combined with a 100
  coin star are given the number 7. Castle stars are given numbers as
  listed
  [here](https://mariopartylegacy.com/guides/super-mario-64-walkthrough/peachs-castle-secret-stars).

## Configuration

To begin configuring the route optimizer, copy the example configuration
file [`config.toml.example`](config.toml.example) to `config.toml` at
the root of the repository:

```bash
cp config.toml.example config.toml
```

Throughout the configuration file, stars are referred to by their unique
IDs. Some examples:

- the first star on Jolly Roger Bay "Plunder in the Sunken Ship" has the
  ID `JRB1`
- the fifth star on Jolly Roger Bay "Blast to the Stone Pillar" has the
  ID `JRB5`
- the 100 coin star combined with a regular course star on Jolly Roger
  Bay has the ID `JRB_100`
- the castle star "The Secret Aquarium" has the ID `CASTLE_AQUA`

The general principle is

- regular course star IDs consist of an acronym of their course name
  (e.g., `JRB` for Jolly Roger Bay) followed by the star's number
- 100 coin combined star IDs have an acronym of their course name
  followed by `_100`
- castle star IDs consist of `CASTLE_` joined with an abbreviation for
  the star (e.g., `AQUA` for "The Secret Aquarium"). These abbreviations
  should be obvious when you see them

A full correspondence of star names with star IDs for non-100 coin
combined stars is available in
[`src/course_data.py`](src/course_data.py).

### Entering times

The first two sections of the configuration file are for entering times.
The first section is for entering regular course and castle star times.
All stars for this section are listed with the following format:

```toml
STAR_ID = []
```

where the array on the right-hand side of the assignment can contain
times (in seconds) as integers or decimal numbers. For example, we can
add three times for the fifth star on Lethal Lava Land "Hot-Foot-It into
the Volcano" by modify the array as follows:

```toml
LLL5 = [48.3, 45, 54.32]
```

The second section is for entering 100 coin combined star times. These
times are for obtaining both the 100 coin star and a regular course star
in a single instance. For each course, there can be at most one star
listed with the format

```toml
COURSE_ID_100 = { times = [], combined_with = "STAR_ID" }
```

where `COURSE_ID` is an acronym of a course name and `STAR_ID` is a
regular course star from that course to be obtained with the 100 coin
star.

A few important notes:

- apart from one special case (see next bullet point), it's okay for
  stars to not have times—they simply won't be included in a route
- since the first star on Dire, Dire Docks "Board Bowser's Sub" is
  required, `DDD1` must have at least one time entered or `DDD_100` must
  have at least one time and be combined with `DDD1`
- omitting times for cap stars precludes stars which require that cap
  from being included in the route[^cap-stage-assumption]

[^cap-stage-assumption]: The program assumes that if we're getting a cap
  (e.g., the wing cap), we're also getting the 8 red coin star on the
  cap stage (e.g., the "Tower of the Wing Cap" star). A consequence of
  this is that if a cap stage star is not included in a route or is
  excluded through either not having a time or a command line argument,
  then all stars it is a prerequisite for are also excluded.

> [!TIP]
> How you record and enter data is up to you. That said, I'd recommend
> using ChatGPT (or other generative AI) to help with this process. For
> recording data, ask for a timer program where you can (1) enter a star
> ID string you can modify and (2) hit a key (not requiring window
> focus) to start and end a timer. Have it record each time along with
> the star ID in a text file. Use this to record star times.
>
> After you've collected times in a text file, show it this file and
> your configuration file, and ask it to integrate the text file times
> into the configuration file time arrays.

### Defining prerequisite relationships

The third and final section of the configuration file is for defining
prerequisite relationships. These relationships are listed with the
following format:

```toml
DEPENDANT_STAR_ID = []
```

where the array on the right-hand side of the assignment contains star
IDs (surrounded by `"`s) which are requirements for `DEPENDANT_STAR_ID`.
For example, the sixth star on Big Boo's Haunt "Eye to Eye in the Secret
Room" requires us to have obtained the first star "Go on a Ghost Hunt"
(for the staircase to the second floor of the haunted house) and the
vanish cap (to enter the room with the eye); this gives us the
prerequisite relationship

```toml
BBH6 = ["BBH1", "CASTLE_VANISH_CAP"]
```

All the mandatory prerequisite relationships are already defined in the
configuration file. It's useful to modify or add to these in two cases:

- you're obtaining a star in an unconventional way. For example, you can
  obtain the third star on Shifting Sand Land "Inside the Ancient
  Pyramid" quickly by going through the top of the pyramid and hopping
  off the elevator inside the pyramid early; to ensure you're able to
  do this, you'd set the wing cap as a prerequisite for this star
- your times for some stars on a course are contingent on an unlocked
  cannon opened on an earlier star. For example, on Bob-omb Battlefield
  if you unlock the cannon on the second star "Footrace with Koopa the
  Quick" and use the cannon on the fourth star "Find the 8 Red Coins"
  and fifth star "Mario Wings to the Sky", you'd set the second star as
  a prerequisite for the fourth and fifth stars. Deciding which star to
  open a cannon on is unfortunately something you need to experiment
  with. It will take some trial and error. For instance, in the above
  example, the second star "Footrace with Koopa the Quick" takes a long
  time, and you're likely better off opening the cannon on a different
  star

> [!IMPORTANT]
> 100 coin combined stars must not be included in prerequisite
> relationships. The program assumes that all 100 coin combined stars
> share the same prerequisite relationships as the regular course stars
> they are combined with.

## Algorithm

The optimization algorithm works in two steps. In the first step, we
exhaustively partition "special stars" into being included in or
excluded from a route; in the second step, we add the fastest
non-special stars to each partial route until a total of 70 stars are
reached. Special stars are stars which are prerequisites or have
alternative stars.[^alternative-stars] We keep track of the fastest
route and return the best one. The algorithm has a time complexity of
$\mathcal{O}(3^n)$, where $n$ is the number of regular course stars and
castle stars which are also special stars.

[^alternative-stars]: Alternative stars come from 100 coin combined
  stars being alternatives to the regular course stars they are combined
  with.

### The first step

In the first step, we begin by placing regular course and castle stars
which are also special stars into an array with the following ordering:
prerequisites first in topologically sorted
order;[^topological-sort-method] then all remaining stars in any order.
We iterate through this array recursively when generating partitions.

We start iterating at the first index with two sets: an "included" set
which contains stars included in the route and an "excluded" set which
contains stars excluded from the route. For each iteration, we
separately include the current star at the index (if possible), include
its 100 coin combined star alternative (if it exists and is possible),
and exclude both the current star and its 100 coin combined star
alternative (if it exists) and their descendants. We then continue the
next iteration using each of these options. A partition is complete
after we iterate through the final index.

Because the first Dire, Dire Docks star "Board Bowser's Sub" is
required, "included" sets are initialized with either the `DDD1` star or
its 100 coin combined star alternative, if it exists.

[^topological-sort-method]: [Kahn's algorithm](https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm)
  is used for topological sorting.

### The second step

In the second step, we sort all eligible stars for the route in
ascending order of their time. We also initialize a min-heap, initially
empty, which will be ordered on star count
requirement.[^star-count-requirement-example]

We start iterating at the first index of the array of stars we sorted.
If the first star is a special star or is excluded from the route, we
skip it. If it is eligible to be in the route, but our current star
count does not meet the star's star count requirement, we push the star
on the heap. Otherwise, we add the star to the route. Each subsequent
iteration proceeds as follows:

- we pop a star from the heap if we meet its star count requirement;
- else, we look at the star under the current index in the sorted array
  of stars:
  - if the star is a special star or excluded, we skip it
  - else, if we do not meet the star's star count requirement, we push
    it on the heap
  - else, we add the star to the route

We continue until we reach a total of 70 stars, and then update the best
route found so far given the sum of star times for the route.

Note that there is additional logic in the second step required to limit
the number of upper level stars if this option was specified as a
command line argument; however, this is not presented here.

[^star-count-requirement-example]: An example of star count
  requirements: because the door leading to Cool, Cool Mountain requires
  three stars to enter, all Cool, Cool Montain stars have a star count
  requirement of at least 3.

## Limitations

This program has several limitations, which are listed in this section.

### Getting a cap stage star is required in logic for getting a cap

See this footnote: [^cap-stage-assumption].

Removing this limitation shouldn't be too difficult. You'd need to
record times separately for getting a cap with and without the cap stage
star. Then, you'd handle the mutually exclusive times similarly to how
regular course stars and their 100 coin combined star alternatives are
handled, which are also mutally exclusive.

My personal opinion is that this limitation is a non-issue.

### 100 coin combined stars can't have unique prerequisites

Suppose on Bob-omb Battlefield that for the 8 red coin star you don't
need the wing cap, but for the 100 coin combined star combined with the
8 red coin star you do need the wing cap. With the current
implementation of prerequisite relationships, you can't have different
prerequisites for regular course stars and their 100 coin combined star
alternatives: all 100 coin combined stars share the prerequisites of the
regular course star they are combined with.

I've given this limitation quite a bit of thought. The algorithm would
need to be modified. In the
[first step of the algorithm](#the-first-step), you would need to
iterate over all special stars—thus including all 100 coin combined
stars which are special stars—and remove the recursive step that
optionally includes a star's 100 coin combined star alternative (since
these are now in the array being iterated over). The topological sort
would also need to be modified, since a star would have multiple
prerequisites it could use. This is all possible though.

The real challenge is designing the configuration file in an elegant way
that avoids excessive complexity and redundancy. For example, one
approach involves listing prerequisites for 100 coin combined stars
separately from the stars they are combined with. In the worst case,
this adds 15 lines to the configuration file that are nearly identical
to 15 other lines. And those lines will need to stay nearly identical—so
when you change one of the lines, you also might need to change the
other line. It's pretty gross, and I haven't come up with ways of
circumventing this limitation that don't involve at least *something*
gross.

### Travel times between courses are not considered

Currently, travel times between courses are not factored into the
optimizer. There are two good options for this I've thought of:

- add a fixed time penalty for entering any given course
- enforce a minimum number of stars to be obtained in a course if it is
  included in a route

Both options are simple in terms of logic and configuration. However,
the computational cost is significant. All of these approaches
algorithmically involve partitioning courses into either being included
or excluded and running the existing algorithm using each possible
partitioning scheme. This increases running time by a factor of $2^{15}
\approx 33000$. Given that the current running time is typically a few
seconds, this would extend runtime to around 2 days.

However, the optimizer is well-suited for parallel processing, since
instances of the optimization algorithm do not need to interact and can
use independent sets of data. This is something to explore in the
future.

## Advice

This section contains advice related to travel times.

### Factoring in travel time for "Vanish Cap Under the Moat"

I discussed previously how travel time between courses isn't
implemented. However, since the vanish cap star "Vanish Cap Under the
Moat" is the only star on its stage and reaching the stage takes a
*long* time, you can manually account for travel time by adding travel
time to the star time in the configuration file.

### MIPS is a menace

The MIPS star becomes available in the basement at 15 stars and again at
50 stars. The second MIPS star that appears at 50 stars can be
problematic. If at 50 stars you're already in the basement, reaching
MIPS is quick. However, if at 50 stars you're already upstairs, travel
time to reach MIPS can be significant. To reach MIPS and get back where
you were, you'd need to enter a course, exit the course through the
start menu to return to the lobby, walk downstairs, capture MIPS, enter
another course, exit again through the menu, and head back upstairs.
Depending on your speed, this can take close to 30 seconds or longer.

The optimizer may generate a route requiring you to return downstairs
for MIPS after you've already left the basement. In this case, it may be
useful to compare the route time with an alternative route that ensures
you can capture MIPS before leaving the basement. To do this, you can
use the flag described in
[Limiting upper level stars](#limiting-upper-level-stars). Note,
however, that limiting the number of upper level stars to 19 isn't
foolproof: for example, you could have an alternative route containing
exactly 50 non-upper level stars, with one of the stars being the sixth
Jolly Roger Bay star "Through the Jet Stream". This still requires you
to leave the basement before capturing MIPS and does not solve the
issue. In such cases, you'd need to adjust the limit further—for
example, to 18 upper-level stars.

