# EthoAnnotator

## Installation
```shell
conda create -n annotator
conda activate -n annotator
conda install pyqtgraph pyside6 numpy matplotlib pyyaml pyvideoreader rich qtpy defopt -c conda-forge
pip install git+https://github.com/janclemenslab/etho_annotator --no-deps
```

## Usage
Start gui with:

- `python -m etho_annotator.app` (will open file open dialog for selecting a video)
- `python -m etho_annotator.app path/to/video.mp4`