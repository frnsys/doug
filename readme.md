- dump svgs into `svg/`
- run `process_svg.py`. this will generate JSON data representing stroke movements that are used to train the neural net.
- `cd` into `nn` and run `train.py` to train the neural net.
- ??? not sure if the whole pipeline works yet

To view a preview drawn from the JSON stroke data, open `preview.html`. Append `#filename.json` to it to load a particular file.