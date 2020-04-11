# Event Definitions 

Event definitions are a little complex, and reading the JSON schema is not very straightforward, so here is an explanation with some more detail as to how everything is meant to work.

## Event Definition Basics

Events are defined in JSON and parsed by the event generator. Below is an example of the simplest event possible:

    {
        "type" : "event",
        "group_name" : "Default",
        "event_type" : "noble",
        "id" : "murdered_commoner",
        "weight" : 1000,
        "actor_defs" : [
            {
                "type" : "noble",
                "var" : "n1"
            }
        ],
        "attach_event" : [ "n1" ],
        "description" : "|n1| was strongly suspected of the murder of a commoner"
    }

This contains every necessary property of an event, and everything in this event definition is required. We'll break it down by property:

`"type" : "event"`
* This is required by every event definition and should always be the same.

`"group_name" : "Default"`
* This is the name which will show up on the main page to allow the user to select groups of events to use. It must exactly match the group you want it to be in, but can be any string.

`"event_type" : "noble"`
* This determines what type of event it is generated as. The three allowed values are `"noble"`, `"courtier"`, and `"family"`.

`"id" : "murdered_commoner"`
* This is the event ID. It must be unique, as only one event definition with any given id will be loaded, in order to prevent accidental duplicates from altering the probabilities of events occurring.

`"weight" : 1000`
* This determines the frequency at which the event will be randomly selected. The base weight I have used is 1000, so any event that you want to occur at the normal rate should have weight 1000. If you want the event to occur less frequently, give it a lower weight. This can be used to, as in the marriage events, adjust specific properties' frequency of occurence, by creating two similar events with different actor requirements and then setting their combined weights to equal 1000. Every 1 weight then becomes 0.1% likelihood for the event going either way. See the "marriage_straight" and "marriage_gay" event definitions in `base-events.json` for an example of generating a lower-probability event based on requirements, in that case equal or unequal "sex" properties.

`"actor_defs" : [
    {
        "type" : "noble",
        "var" : "n1"
    }
],`
* This is an array defining what I've called "actors", which are nobles, courtiers, or families that are selected based on constraints (which I have called "requirements") and are then inserted into the description string to make the event. This is the simplest possible actor definition - one actor, with a type and variable.
    * Every actor definition is *required* to have the following properties:
        * `"type"`: may be `"noble"`, `"courtier"`, or `"family'`, corresponding to the objects of the same names in the realm generator
        * `"var"`: is used as a token in the `"description"`, where it will be replaced with the actor's name; may be any string except the following:
            * `"faction"`
            * `"animal"`
            * `"adjective"`
            * any other defined actor variable 
            * any defined random token (discussed further in their own section)
    * Noble and Courtier actors may have additional optional variables defined:
        * `"noble"` and `"courtier"` type actors may have a `"family_var"` variable set, which will be replaced with the name of the family they are members of; this has the same restrictions as the actor's `"var"`
        * `"courtier"` type actors may have a `"position_var"` variable, which will be replaced with their position; this has the same restrictions as the actor's `"var"`

`"attach_event" : [ "n1" ]`
* This lists the actor variables representing the objects to which the event should be attached - any variable listed here will have the event appended to the corresponding object's events list. There must be at least one valid entry in the list or the event visible after the realm is generated.

`"description" : "|n1| was strongly suspected of the murder of a commoner"`
* This is the event description text, with tokens bracketed by the `|` character. Anything bracketed by the `|` character becomes a token, and if an actor variable exists with a matching string, that token will be replaced by the actor's name. There are a few special tokens: 
    * `|faction|` will be replaced by a randomly selected faction
    * `|animal|` will be replaced by a randomly selected animal
    * `|adjective|` will be replaced by a randomly selected adjective
    * random tokens can be defined, which will replace the token with a random selection from a list provided in the event definition.
    If the token is not found in the actor variables or random tokens, then the `|` characters will be stripped and the token will be put back into the description as it appears; if there was no `"n1"` actor variable available for this description to use, the description would literally read *"n1 was strongly suspected of the murder of a commoner"*.

Very similarly to the above example, here are examples of two of the most basic family and courtier events:

    {
        "type" : "event",
        "group_name" : "Default",
        "event_type" : "family",
        "id" : "uprising",
        "weight" : 1000,
        "actor_defs" : [
            { "type" : "family", "var" : "f1" }
        ],
        "attach_event" : [ "f1" ],
        "description" : "An uprising of smallfolk has taken hold against the |f1|"
    }

    {
        "type" : "event",
        "group_name" : "Default",
        "event_type" : "courtier",
        "id" : "duel",
        "weight" : 1000,
        "actor_defs" : [
            { "type" : "courtier", "var" : "c1", "position_var": "c1p" },
            { "type" : "noble", "var" : "n2", "family_var" : "f2" }
        ],
        "attach_event" : [ "c1", "n2" ],
        "description" : "|c1| (|c1p|) was killed by |n2| of the |f2| in a duel of honour"
    }

The simple family event is pretty much the same as the previous example of a noble event, but you can see that the courtier event has two actors defined, each with an additional variable - the noble has its `family_var`, and the courtier has its `position_var`.

Families are special, in that they can have actor definitions inside of them, in an array called `"member_defs"`, as seen in the example below:

    {
        "type" : "event",
        "group_name" : "Default",
        "event_type" : "courtier",
        "id" : "hung",
        "weight" : 1000,
        "actor_defs" : [
            { 
                "type" : "family", "var" : "f1", "member_defs" : [
                    { "type" : "courtier", "var" : "c1", "position_var": "c1p" },
                    { "type" : "noble", "var" : "n1" }
                ]
            }
        ],
        "attach_event" : [ "c1", "n1" ],
        "description" : "|c1| (|c1p|) was executed by |n1|"
    }

The contents of the `"member_defs"` array of a family works just like regular `"actor_defs"`, except that when the actors are generated they are guaranteed to be selected from the family's nobles and courtiers, instead of randomly from the entire population.

## Actor Requirements 

Actors of any kind can also have requirements attached to them, a simple case is shown below:

    {
        "type" : "event",
        "group_name" : "Default",
        "event_type" : "noble",
        "id" : "baby",
        "weight" : 1000,
        "actor_defs" : [
            {
                "type" : "noble",
                "req_gt" : { "age" : 18 },
                "var" : "parent"
            }
        ],
        "attach_event" : [ "parent" ],
        "description" : "A baby was born to |parent|"
    }

There are a couple of things to note here. First, you can see that the actor's `"var"` is indeed a freeform string, it has been labelled `"parent"` here. As noted above, with a small handful of exceptions you can use any variable name you want to. The other thing to note is that this actor has a requirement - specifically, it includes the property `"req_gt" : { "age" : 18 }`. There are several requirements that can be used, listed below. This one means that only nobles with the property `"age"` greater than 18 can be selected for this event. If there was another property you wanted to make sure the actor was larger than (say, if a "height" property existed), you could add that to this same object, like `"req_gt" : { "age" : 18, "height" : 60 }`. You can not have more than one of any requirement property inside of the same actor (e.g. you can't have two "req_gt" properties on the same actor), you must include all the things you want to perform the same check on in the one property (in this case all "attribute greater than" requirements).

The individual actor requirements that you can use are below:
### Individual Actor Requirements
* `"req_eq"`
    * Require that an actor's attributes exactly match the properties given. The actor may have additional properties that are not listed, but if they do not have all of the properties listed matching exactly, they will not be selected.
    * Example: `"req_eq" : { "sex" : "female" }`
        * Actor will be female.
* `"req_not_eq"`
    * Require that an actor's attributes do not match the properties given. The actor may have additional properties that are not listed, but if any of their properties match the requirement, they will not be selected.
    * Example: `"req_not_eq" : { "sex" : "female" }`
        * Actor will not be female.
* `"req_gt"`
    * Require that an actor's attributes are greater than the properties given. This will perform a Python > between the given value and the attribute, so will work for e.g. lexographically ordered string comparisons as well as numbers.
    * Example: `"req_gt" : { "age" : 18 }`
        * Actor will have an age greater than 18
* `"req_lt"`
    * Require that an actor's attributes are less than the properties given. This will perform a Python < between the given value and the attribute, so will work for e.g. lexographically ordered string comparisons as well as numbers.
    * Example: `"req_lt" : { "age" : 18 }`
        * Actor will have an age less than 18
* `"req_in"`
    * This requires each property given to have an array of values, which the actor's attribute will be checked against to ensure that the actor's attribute is contained in the list provided by the definition.
    * Example: `"req_in" : { "race" : [ "Tortle", "Lizardfolk", "Triton" ] }`
        * Actor will have the race "Tortle", "Lizardfolk", or "Triton"
* `"req_not_in"`
    * This requires each property given to have an array of values, which the actor's attribute will be checked against to ensure that the actor's attribute is not contained in the list provided by the definition.
    * Example: `"req_not_in" : { "race" : [ "Tortle", "Lizardfolk", "Triton" ] }`
        * Actor will not have the race "Tortle", "Lizardfolk", or "Triton"
* `"req_has"`
    * Require that the actor has the given attributes and that they have values (i.e. are not `None`).
    * Example: `"req_has" : [ "post_nickname" ]`
        * Actor will have a post_nickname
* `"req_not_has"`
    * Require that the actor does not have the given attributes or that if they do the attributes do not have values (i.e. are `None`)
    * Example: `"req_not_has" : [ "post_nickname" ]`
        Actor will not have a post_nickname
* `"req_len_gt"` 
    * Require that the actor's attribute has a number of items greater than the number given. This is primarily of concern when defining family events to ensure that the family has enough courtiers, persons, vassals, etc. It could also be used to limit the number of events assigned to an actor.
    * Example: `"req_len_gt" : { "courtiers" : 1, "persons" : 0 }`
        * Actor will have at least two courtiers and at least one persons
* `"req_len_lt"`
    Require that the actor's attribute has a number of items less than the number given.
    * Example: `"req_len_lt" : { "knights" : 1, "vassals" : 1 }`
        * Actor will have fewer than 1 knights and fewer than 1 vassals.

See below for an example of an event with most of the requirements on a single actor, which was used while testing:

    {
        "type" : "event",
        "group_name" : "Test",
        "id" : "very_specific_contest",
        "weight" : 1000,
        "event_type" : "noble",
        "actor_defs" : [
            {
                "type" : "noble", "var" : "n1", "family_var" : "f1",
                "req_eq" : { "sex" : "female" },
                "req_not_eq" : { "leader_relation" : "wife" },
                "req_gt" : { "age" : 20 },
                "req_lt" : { "age" : 30 },
                "req_in" : { "race" : [ "Tortle", "Lizardfolk", "Triton" ] },
                "req_not_in" : { "alignment_print" : [ "Lawful Evil", "Neutral Evil", "Chaotic Evil" ] },
                "req_has" : [ "post_nickname" ],
                "req_not_has" : [ "pre_nickname" ]
            }
        ],
        "attach_event" : [ "n1" ],
        "description" : "|n1| won a contest with suspiciously specific requirements"
    }

This defines an actor who is: a noble; female; not the family leader's wife; between the ages of 20 and 30; a Tortle, Lizardfok, or Triton; not Evil aligned; and has a nickname after her name, but not before it. Seems like a setup to me.

## Required Matches 

In addition to individual actor requirements, you can also define requirements that take into account multiple actors. See the below event definition:

    {
        "type" : "event",
        "group_name" : "Default",
        "event_type" : "courtier",
        "id" : "office_swap",
        "weight" : 1000,
        "actor_defs" : [
            {
                "type" : "family", "var" : "f1",
                "req_len_gt" : { "courtiers" : 1, "persons" : 0 },
                "member_defs" : [
                    { "type" : "courtier", "var" : "c1", "position_var" : "c1p" },
                    { "type" : "courtier", "var" : "c2", "position_var" : "c2p" },
                    { "type" : "noble", "var" : "n1" }
                ]
            }
        ],
        "req_matches" : [
            {
                "actors" : [ "c1", "c2" ],
                "req_actors_any_neq" : [ "pre_nickname", "firstname", "post_nickname" ]
            }
        ],
        "attach_event" : [ "c1", "c2" ],
        "description" : "|c1| (|c1p|) and |c2| (|c2p|) have swapped offices by order of |n1| of |f1|"
    }

There's a lot there, but we've already been through what most of it means. This is a normal weight courtier event named office_swap, and it defines four actors: a family with at least 2 courtiers and 1 noble, and then two courtiers and a noble who are members of that family. You can also see that the courtiers' positions are taken as variables `"c1p"` and `"c2p"` and used in the description string, along with the noble and family name. The event is attached to both of the courtiers, but not to the noble.

Below the actor_defs, you can see a new event defintion property that we have not discussed before: `"req_matches"`. This is an array of objects, in which each object defines a group of actors and what must or must not match between them. In this case, it applies the requirement to the actors `"c1"` and `"c2"`, and requires that any one of their `"pre_nickname"`, `"firstname"`, or `"post_nickname"` must not match. The word "any" is important there; if two of the three things match but the third one doesn't, then that will still be an OK selection. This particular requirement is to ensure that the same actor is not picked - if any of those three attributes are different, then it's a different person. The same requirement with `"family_name"` added is used to ensure that two nobles are different people in some events.

Note that if desired, the noble and either courtier (or the noble and both courtiers) could be added in separate object in the `"req_matches"` array, to apply different match requirements to those groups. You may have as many groups as you want in the `"req_matches"` array, but if it is present you must have at least one. The `"actors"` array requires at least two items or it will be ignored, because it doesn't make sense to check that something is or is not equal to itself.

There are several matching requirements that can be used:
### Match Requirements
* `"req_actors_any_eq"`
    * Requires that all of the actors have any of the listed attributes matching.
    * Example: `"req_actors_any_eq" : [ "sex", "alignment" ]`
        * This will match if all of the actors have matching sex or alignment (or both)
* `"req_actors_any_neq"`
    * Requires that all of the actors have any of the listed attributes not matching.
    * Example: `"req_actors_any_neq" : [ "pre_nickname", "firstname", "post_nickname", "family_name" ]`
        * This will match if all of the actors have any part of their name that isn't the same. It is used frequently to guarantee unique actors in events with two actors.
* `"req_actors_all_eq"`
    * Requires that all of the actors have all of the listed attributes matching.
    * Example: `"req_actors_all_eq" : [ "sex" ]`
        * This will match if the actors are all the same sex.
* `"req_actors_all_neq"`
    * Requires that all of the actors have all of the listed attributes not matching.
    * Example: `"req_actors_all_neq" : [ "sex" ]`
        * This will match if none of the actors are the same sex. Unless you have modified the realm generator software (which at this time only contains two sexes), this will only work for two actors at a time.
* `"req_vassalage"`
    * Requires that one of the actors is a vassal of the other. This is different from the other match requirements, in that it only applies to two actors at a time and is formatted as an object with properties "lord" and "vassal".
    * Example: `"req_vassalage" : { "lord" : "f1", "vassal" : "f2" }`
        * This will match if `"f2"` is a vassal (knight or vassal) of `"f1"`

## Random Tokens

As was previously stated, descriptions can include several different types of tokens: actor variables; the special tokens `|faction|`, `|animal|`, and `|adjective|`; and random tokens. Random tokens are defined in the event definition with a list of replacements which get chosen from when the event is generated. See an example below:

    {
        "type" : "event",
        "group_name" : "Signs & Omens",
        "event_type" : "noble",
        "id" : "strange-colored-fire",
        "weight" : 100,
        "actor_defs" : [
            { "type" : "noble", "var" : "n", "family_var" : "f" }
        ],
        "attach_event" : [ "n" ],
        "random_tokens" : { "color" : [ "blue", "green", "purple", "white", "pink" ] },
        "description" : "A fire was seen turning |color| when |n| approached"
    }

You can see that it has a `"random_tokens"` property, which is an object named `"color"` and an array of colors. The description then contains the token `|color|`. When the event is generated, a color will be selected at random from the list and used in place of the `|color|` token. This is a `random.choice()` selection, so it will be equally weighted; if you want to weight your choices, then the only current method of doing so is to add more entries in proportion to the desired weights. If I had put `"blue"` in four times, it would have a 50% chance of being chosen, but since I did not it will be chosen 20% of the time.

The random tokens are processed and replaced before the other variables, which lets you replace a random token with an actor variable (or special token). See the below example:

    {
        "type" : "event",
        "group_name" : "Default",
        "event_type" : "noble",
        "id" : "honour_duel",
        "weight" : 1000,
        "actor_defs" : [
            {
                "type" : "noble",
                "req_gt" : { "age" : 17 },
                "var" : "n1",
                "family_var" : "f1"
            },
            {
                "type" : "noble",
                "req_gt" : { "age" : 17 },
                "var" : "n2",
                "family_var" : "f2"
            }
        ],
        "req_matches" : [
            {
                "actors" : [ "n1", "n2" ],
                "req_actors_any_neq" : [ 
                    "pre_nickname", 
                    "firstname", 
                    "post_nickname", 
                    "family_name" 
                ]
            }
        ],
        "attach_event" : [ "n1", "n2" ],
        "random_tokens" : { "winner" : [ "n1", "n2" ] },
        "description" : "|n1| of the |f1| dueled with |n2| of the |f2|; |winner| won"
    }

This is quite long, and shows off many of the things we have discussed so far. The part that is most interesting at this point is at the bottom. You can see that the random_tokens defines a token named `"winner"` that can be `"n1"` or `"n2"`, which are the same as the two actor variables. When the event is being generated, the random tokens will be processed first, so `|winner|` will get replaced with either `n1` or `n2`. Then, when the actor variables are processed, that token will be treated as if it was always the actor variable, so we can have a random winner of the duel. Note that when used in this way the random token list should not include the `|` characters - those are stripped in an earlier step, and will result in the description including them literally as `"|n1|"` or `"|n2|"`.

There is an alternate method of acheiving this same behavior: create two events that are the same, but with different ids and a different actor token in the description, and then give them each half of the weight. 

## More Examples 

Reading over the existing event definitions in the `"base-events.json"` and `"events-omens.json"` files in the words directory should give you a good understanding of what the various features are being used for, but every feature of the event definition system is not represented in them. Below are some events that I used during testing, which show off some of the features and ways to do things. Note that these are also not exhaustive, and I'm sure that there are clever or interesting ways to use the various features that I have not discovered myself. For testing new events, I have found that it is easiest to turn off all non-test events and generate a realm with 1 Great, 1 Minor, and 1 Petty house; this guarantees you will get very long lists on each house page containing many of your test events.

    {
        "type" : "event",
        "group_name" : "Test",
        "id" : "tournament_sexism",
        "weight" : 1000,
        "event_type" : "noble",
        "actor_defs" : [
            {
                "type" : "noble",
                "req_eq" : { "sex" : "female" },
                "var" : "n1",
                "family_var" : "f1"
            }
        ],
        "attach_event" : [ "n1" ],
        "description" : "|n1| was caught trying to compete in a tournament as a man"
    },
    {
        "type" : "event",
        "group_name" : "Test",
        "id" : "impotence_rumors",
        "weight" : 1000,
        "event_type" : "noble",
        "actor_defs" : [
            {
                "type" : "noble",
                "req_not_eq" : { "sex" : "female" },
                "var" : "n1",
                "family_var" : "f1"
            }
        ],
        "attach_event" : [ "n1" ],
        "description" : "Rumors have spread that |n1| is impotent"
    },
    {
        "type" : "event",
        "group_name" : "Test",
        "id" : "drow_are_too_edgy",
        "weight" : 1000,
        "event_type" : "noble",
        "actor_defs" : [
            {
                "type" : "noble",
                "req_eq" : {  "race" : "Elf (Drow)" },
                "var" : "n1",
                "family_var" : "f1"
            }
        ],
        "attach_event" : [ "n1" ],
        "description" : "|n1| died of bloodloss after getting cut on all their edginess"
    },
    {
        "type" : "event",
        "group_name" : "Test",
        "id" : "racism_against_dwarves",
        "weight" : 1000,
        "event_type" : "noble",
        "actor_defs" : [
            {
                "type" : "noble",
                "req_not_in" : { 
                    "race" : [
                        "Dwarf (Duergar)",
                        "Dwarf (Hill)",
                        "Dwarf (Mark of Warding)",
                        "Dwarf (Mountain)" ]
                },
                "var" : "n1",
                "family_var" : "f1"
            }
        ],
        "attach_event" : [ "n1" ],
        "description" : "|n1| was heard loudly proclaiming all Dwarves to be greedy thieves"
    },
    {
        "type" : "event",
        "group_name" : "Test",
        "id" : "marie_antoinette",
        "weight" : 1000,
        "event_type" : "noble",
        "actor_defs" : [
            {
                "type" : "noble",
                "req_not_in" : { 
                    "rank" : [ "petty", "minor", "great" ]
                },
                "var" : "n1",
                "family_var" : "f1"
            }
        ],
        "attach_event" : [ "n1" ],
        "description" : "|n1| was overheard asking why starving peasants didn't just eat brioche"
    },
    {
        "type" : "event",
        "group_name" : "Test",
        "id" : "jealous_nicknames",
        "weight" : 1000,
        "event_type" : "noble",
        "actor_defs" : [
            {
                "type" : "noble",
                "req_not_has" : [ "pre_nickname", "post_nickname" ],
                "var" : "jelly"
            }
        ],
        "attach_event" : [ "jelly" ],
        "description" : "|jelly| made a failed attempt to ban the use of nicknames"
    },
    {
        "type" : "event",
        "group_name" : "Test",
        "id" : "feud_start",
        "weight" : 1000,
        "event_type" : "noble",
        "actor_defs" : [
            { "type" : "noble", "var" : "n1", "family_var" : "f1" },
            { "type" : "noble", "var" : "n2", "family_var" : "f2" }
        ],
        "req_matches" : [
            {
                "actors" : [ "n1", "n2" ],
                "req_actors_any_eq" : [ "sex" ]
            },
            {
                "actors" : [ "f1", "f2" ],
                "req_actors_all_neq" : [ "name" ]
            }
        ],
        "attach_event" : [ "f1", "f2" ],
        "description" : "|f1| and |f2| started feuding over a dispute between |n1| and |n2|"
    },
    {
        "type" : "event",
        "group_name" : "Test",
        "event_type" : "courtier",
        "id" : "petty_fistfight",
        "weight" : 1000,
        "actor_defs" : [
            { 
                "type" : "family", "var" : "f1",
                "member_defs" : [
                    { "type" : "courtier", "var" : "c1", "position_var" : "c1p" },
                    { "type" : "courtier", "var" : "c2", "position_var" : "c2p" }
                ]
            }
        ],
        "req_matches" : [
            {
                "actors" : [ "c1", "c2" ],
                "req_actors_any_neq" : [ "pre_nickname", "firstname", "post_nickname" ]
            }
        ],
        "attach_event" : [ "c1", "c2" ],
        "description" : "|c1| got into a fistfight with |c2| after |c2| called |c1p| a pointless job"
    },
    {
        "type" : "event",
        "group_name" : "Test",
        "event_type" : "family",
        "id" : "family_gone_crazy",
        "weight" : 1000,
        "actor_defs" : [
            { "type" : "family", "var" : "f" }
        ],
        "attach_event" : [ "f" ],
        "description" : "The |f| has dissolved after donating all of their land to |faction| and leaving to follow a |animal|. They were heard calling the rest of the nobility |adjective| on their way off."
    }