[![Build Status](https://travis-ci.com/JohnPaton/nbviewerbot.svg?branch=master)](https://travis-ci.com/JohnPaton/nbviewerbot)


# nbviewerbot

A Reddit bot to convert GitHub Jupyter Notebook URLs to [nbviewer](https://nbviewer.jupyter.org/) links for mobile notebook rendering.

> *jd_paton*:
>
> Check out my cool notebook: https://github.com/JohnPaton/numpy-neural-networks/blob/master/01-single-layer-perceptron.ipynb
>
>> *nbviewerbot*:
>>
>> I see you've posted a GitHub link to a Jupyter Notebook! GitHub doesn't 
render Jupyter Notebooks on mobile, so here is an 
[nbviewer](https://nbviewer.jupyter.org/) link to the notebook 
for mobile viewing:
>> 
>> https://nbviewer.jupyter.org/url/github.com/JohnPaton/numpy-neural-networks/blob/master/01-single-layer-perceptron.ipynb
>> 
>> -----
>> 
>> I am a bot. [Feedback](https://www.reddit.com/message/compose/?to=jd_paton) | [GitHub](https://github.com/JohnPaton/nbviewerbot) | [Author](https://johnpaton.net/)


## Installation

To install `nbviewerbot`, first clone this repository, and then install it in edit mode using `pip`:
```bash
$ git clone git@github.com:JohnPaton/nbviewerbot.git
$ cd nbviewerbot
$ pip install -e .
```

Before running, you must register a script application with Reddit. You must also give this application access to an account for the bot to post from. Please follow the instructions [here](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps). Once you have done this, you must store the account's username and password, and your app's client id and client secret in a `.env` file in the package's `nbviewerbot` directory. A template for this file is provided at `nbviewerbot/.env_template`. **Note**: If you do not install in edit mode (i.e. without pip's `-e` option) then you must reinstall the package (`pip install --upgrade .`) every time you change the `nbviewerbot/.env` file, or change it directly in your system's install location. You can also provide a custom `.env` file at runtime (see [Usage](#usage)).

If you want to run the tests, you can do so with `pytest` (for your current environment) or `tox` (for available `python3` environments).


## Usage
Once you have `pip` installed `nbviewerbot`, you can run it from the command line with the command `nbviewerbot`. This will watch a default list of relevant subreddits for comments containing GitHub links to Jupyter Notebooks, and reply to them with a comment containing a nbviewer link for each Jupyter link in the parent. 
```
$ nbviewerbot
2018-08-05 11:35:43,729 INFO - Successfully authenticated with Reddit
2018-08-05 11:35:43,729 INFO - Streaming comments from algotrading+analytics+askmath+askprogramming+aws+beginnerprojects+bigdata+bioinformatics+businessintelligence+codeprojects+computervision+coolgithubprojects+cs231n+datacleaning+dataisbeautiful+datamining+datascience+datasciencenews+deepdream+deeplearners+deeplearning+github+ipynb+ipython+jupyter+jupyternotebooks+languagetechnology+learnmachinelearning+learnprogramming+learnpython+machinelearning+mlquestions+nlp+programming+pyfinance+pystats+python+pythontips+rstats+science+simulate+statistics+tensorflow
2018-08-05 11:35:43,730 INFO - Started nbviewerbot, listening for new comments...
```

To view the available subreddit lists, use the command `nbviewerbot subreddits`. The default list is the testing list plus a [list of relevant subreddits](https://github.com/JohnPaton/nbviewerbot/blob/master/nbviewerbot/resources.d/subreddits.txt). Additions to this list would be welcome, feel free to open a PR!

For more details on the command line interface, please use the `--help` argument:

```
$ nbviewerbot --help
Usage: nbviewerbot [OPTIONS] COMMAND [ARGS]...

  Run the nbviewerbot on the selected subreddit set.

Options:
  -v, --verbose                   Show DEBUG logs (always available at
                                  /path/to/nbviewerbot/nbviewerbot.log)
  -q, --quiet                     Don't show any command line output
  -s, --subreddit-set [relevant|test|all]
                                  Set of subreddits to use. Options:
                                  "relevant" (default, only relevant
                                  subreddits), "all" (/r/all),  or "test" (bot
                                  testing subreddits). Use the "nbviewerbot
                                  subreddits" command to view the complete
                                  lists.
  -e, --env PATH                  A custom .env file for loading environment
                                  variables. Relevant vars: CLIENT_ID,
                                  CLIENT_SECRET, USERNAME, PASSWORD.
  --help                          Show this message and exit.

Commands:
  subreddits  Show subreddits used by the -s options
```
