# usage

First you have to train a drawing model:

    ./doug.py train [model name] [svg folder]

    # example
    ./doug.py train calligraphy calligraphy_svgs

Then you can use that model to generate drawing data:

    # after training a model
    ./doug.py draw [model name] [number of points]

    # example
    ./doug.py draw calligraphy 1000

To view a preview drawn from the JSON stroke data, open `preview.html`. Append `#filename.json` to it to load a particular file in the `drawings` folder. If you don't specify a file, it will try to load `drawings/0000.json`.

<https://commons.wikimedia.org/w/index.php?title=Special:Search&limit=500&offset=0&profile=default&search=line+drawing+svg&searchToken=858sogt2izud1zwltfuemoj0u>