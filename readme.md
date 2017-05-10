# usage

First you have to train a drawing model:

    ./doug.py train [model name] [svg folder]

    # example
    ./doug.py train calligraphy calligraphy_svgs

You might get an error if the `batch_size` is too small. When the neural network is preparing to train it will output the number of available batches (`batches`) and the specified batch size (`batch size`). If `batch size > batches` then you will get this error. To fix it, re-run the command with a smaller batch size, e.g.:

    ./doug.py train calligraphy calligraphy_svgs --batch_size 16

Then you can use that model to generate drawing data:

    # after training a model
    ./doug.py draw [model name] [number of points]

    # example
    ./doug.py draw calligraphy 1000

To view a preview drawn from the JSON stroke data, open `preview.html`. Append `#filename.json` to it to load a particular file in the `drawings` folder. If you don't specify a file, it will try to load `drawings/0000.json`.

# converting json to svg

If you need to convert a JSON file of steps to SVG, you can use `json2svg.py`. For example:

    ./json2svg.py test.json

---

<https://commons.wikimedia.org/w/index.php?title=Special:Search&limit=500&offset=0&profile=default&search=line+drawing+svg&searchToken=858sogt2izud1zwltfuemoj0u>

---

tips:

- if getting `nan` during training, try increasing the data scale or decreasing the learning rate
- if the training doesn't appear to work (no epochs are reported) you may need to decrease the batch size