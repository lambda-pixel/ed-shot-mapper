# ED Screenshot Mapper
This is a small utility to retrieve location of screeshots from your CMDR journal.

## Disclaimer
This is a quick and dirty written script. While it shall not overwrite and mess up your files, use it at your own risk ;-)

## Usage
Just download the lastest executable from the Releases. Then, you'll need to drag and drop a folder or a `.bmp` or `.jpg` file on the executable. It will create a `out` folder with a copy of the files next to the executable.

You can also use the CLI to provide the path of the file you want to tag

If you directly download the Python file, you just have to gives in the command the location of the image or folder of images you'd like to tag.

```bash
python ed-shot-mapper.py screenshot.jpg
```

## Future plans
If finding time to enhance the application, would be nice to further detail the position (station / body) and provide an option to let user format the output.