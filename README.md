## mara_nlp_suite

This repository encompasses the unified NLP research platform for the project [MARA: MEDIA REPORTING ON ALGORITHMS, ROBOTICS AND ARTIFICIAL INTELLIGENCE](https://www.oeaw.ac.at/cmc/research/media-accountability-media-change-mamc/media-ethics-and-media-accountability/triple-a-algorithms-automation-accountability/risks-and-responsibility-in-the-automation-debate-mara/) funded by the Austrian Academy of Sciences’ [go!digital Next Generation program for excellent research in digital humanities](https://www.oeaw.ac.at/foerderungen/godigital/godigital-next-generation).

In this repo almost all code and (soon) nlp models are stored and published in a transparent and reproducible way.

**This repository is work in progress! Hence for now there are following limitations:**

* no original newspaper texts are stored here due to pending coypright agreements
* no nlp models are stored yet due to technical limitations in terms of storage of github (soon to come)
* little technical documentation, no comments, and on no guarantee on full stability (soon to come)


## External dependencies / sources and tools:

* [Python](https://www.python.org/): main language in this project
* [spaCy](https://spacy.io/): NLP ML platform
* [prodigy](http://prodi.gy/): text annotation tool
* [sketchengine](https://www.sketchengine.eu/): linguistic content archive
* [Austrian Media Corpus](https://www.oeaw.ac.at/acdh/tools/amc-austria-media-corpus): archive of austrian newspaper texts


## Architecture and Overview

### Rough outline of architecture

```
 +----------------------------+ 
 | data flow registry         |-----------+
 | * central reference hub    |           | references functions / classes
 | * machine usable           |           | 
 | * human readable           |           |
 +----------------------------+           |
  ^                                       |
  | references config details             |
  |                                       |
 +----------------------------+           |
 | pipes                      |           |
 | * high abstraction overview|           |
 | * collection of processes  |           |
 +----------------------------+           |
  |                                       |
  | calls                                 |
  v                                       |
 +------------------+                     |
 | main             |                     |
 | * code hub       |                     |
 +------------------+                     |
  |                                       |
  | delegates                             |
  |                                       |
  |      +-----------------------+        |
  +----->| ETL                   |<-------+
  |      | * fetch raw data      |        |
  |      | * transform and clean |        |
  |      | * persist clean data  |        |
  |      +-----------------------+        |
  |                                       |
  |      +-----------------------+        |
  +----->| Annotation            |<-------+
  |      | * human labeling      |        |
  |      | * human verification  |        |
  |      +-----------------------+        |
  |                                       |
  |      +-----------------------+        |
  +----->| NLP                   |<-------+
  |      | * ML training         |        |
  |      | * ML classification   |        |
  |      +-----------------------+        |
  |                                       |
  |      +-----------------------+        |
  +----->| Evaluation            |<-------+
         | * statistical analysis|
         | * presentation        |
         +-----------------------+
```

### The major modules in this research context can be separated into:
* pipes & data flow registry: encapsulating configurations and processes with high degree of abstraction
* ETL: Responsible for all tasks relating to fetching and transforming data from various sources
* Annotation: providing accessible means for humans to annotate and verify data
* NLP Training: using supervised machine learning on topic modelling and classification 
* Evaluation: of trained nlp models and human verification of them

### Pipeline architecture

Since the research task is an iterative process with continous feedback, the technical requirements can change rapidly. Thus the platform needs to be able to adapt to changes, while being reusable as well. For this, we implemented a pipeline architecture, which means that major tasks are encapsulated in various modules and can be called and chained together in various `pipes`. For example a pipe could first define to fetch data, transform it to pre defined rules, and then run a training on it. All of such pipes are defined under [src/pipelining/pipes](src/pipelining/pipes).

### data flow registry

This registry in [src/pipelining/data_flow_registry.py](src/pipelining/data_flow_registry.py) serves as the single source of truth to define and preserve which data was processed by which computation with which parameters. 

The registry is used both by:
* machines: pipes use references from the registry to fetch data and call registered functions
* humans: to document and reconstruct data flows for transparancy and reproducibility

Everything that is persisted or fetched is registered there. 

Additionally in this registry we define and document:
* all data inter-dependencies: e.g. which texts were used for which models, which data sets came from where, which models evaluated what texts, et cetera
* transformations on data: e.g. what classifications were changed and bundled into others or discarded completely
* code logic: which functions were used for processing what data


## How to set up

**DISCLAIMER: There are no models and texts yet, which sadly renders this repo to little use for the public. Work is under way to mitigate this and to provide useful data and models.**

First, clone this repo and change into it. 

```
git clone https://github.com/acdh-oeaw/mara_nlp_suite.git
cd mara_nlp_suite
```

Then there are two ways of running this suite: docker or native python (where virtual environments are recommended).

### Building and running with docker

A pre-built docker image is yet to be published on docker hub. Until then, a local image can be built by changing into the root directory and build with:
```
docker build . -t image_mara_nlp_suite    # will take a while, since pre-learned nlp models are downloaded
docker run -it image_mara_nlp_suite bash    # run and enter container
```

### Setting up with native python (tested only under linux)

While it can be set up with bare metal python, we recommend to use python virtual environemnts for the sake of system hygiene. 
Assuming virtualenv is installed, then do in the root directory of this repo:
```
virtualenv -p python3.8 venv    # create virtual environment
source venv/bin/activate    # activate it
pip install -r requirements.txt    # install python dependencies, will take a while, since pre-learned nlp models are downloaded
```

## How to run

Either inside the docker container or on your machine with a python virtual environment, change to the src directory and run an arbitrary pipe from [src/pipelining/pipes](src/pipelining/pipes). To run an interactive shell, use the pre-defined `pipe_shell`:
```
cd src
python main.py --pipe pipe_shell    # replace the pipe argument with the name of any module in `pipes`.
```

**TODO: Add examples once useful data is made public**

## non-functional components / dependencies:

The following components of this repo will remain non-functional to the public for the foreseeable future (unless you own the respective licenses / have credentials):

* The internally used tool [prodigy](http://prodi.gy/) is proprietary and was purchased for this research task.
* The newspaper texts are all fetched from the internal [Austrian Media Corpus](https://www.oeaw.ac.at/acdh/tools/amc-austria-media-corpus) accessed with [sketchengine](https://www.sketchengine.eu/).
