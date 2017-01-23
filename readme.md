- dump svgs into `svg/`
- run `process_svg.py`. this will generate JSON data representing stroke movements that are used to train the neural net.
- `cd` into `neuralnet` and run `train.py` to train the neural net.
- then run `sample.py` to generate `sample.json`, a sample drawing from the net

To view a preview drawn from the JSON stroke data, open `preview.html`. Append `#filename.json` to it to load a particular file. If you don't specify a file, it will load the `sample.json` produced by the net.