# The Realm Generator
If you've ever played a tabletop roleplaying game, then you may have encountered a common problem: you haven't got the time to invent a realm. And I don't mean a realm with a single great dynasty in it; I mean *hundreds* of noble families, *thousands* of nobles and courtiers, complex relationships between them, feuds, alliances, loose factions, hierarchies...it's work.

That is, it was work. Until now. Presenting...

### The Realm Generator.

In a single click, you can generate a complex, interwoven realm filled with intrigue, ready for any tabletop gaming experience.

[In fact, you can do it right now, without having to build anything. Check it out!](https://infinite-woodland-34884.herokuapp.com/)

## Building

Building the code is easy enough. Assuming the use of Python 3, check out the code, change to the source directory, and then:

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    export FLASK_APP=app.py
    flask run

And, you're running. Easy peasy.

## Pull Requests

Pull requests are welcome. Here are a few things that I'd like to work on, but probably won't:

- Migrating the front-end to a front-end framework.
  - Right now, all of the front-end is generated using raw HTML generators. This is messy and is not maintainable.
  - A better solution would be to use a front-end framework, such as React or AngularJS, to render the pages.
- Making the event generator a parser of markup files, rather than a series of functions.
  - event.py is just a very long list of functions that generates different kind of events.
  - Although this is fine, a solution that would be more easy to extend would be to make a markup schema for events (in YAML or whatever), and make event.py a parser of this schema which can then generate events.
- Making a list of realm names.
  - Realms have no names. Oh, well. You can make up your own or use a generator. Eventually, though, I'd like a list of realms that generate a name for the generated realm. Makes sense, yeah.
- Migrate everything in the "word" directory from native python lists into markup files.
  - A cosmetic change, mostly.
## A few notes on names

In general, names were chosen that were easy to pronounce for a North American English native speaker. Furthermore, a lot of guesses were made about things that have to do with foreign historical civilisations; mistakes are certain to have been made.
