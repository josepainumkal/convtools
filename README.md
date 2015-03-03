# Virtual Watershed Platform (VWP)

In order to address the needs of the watershed modelers we work with,
this is the virtual watershed platform. So far we have a minimal
search interface, shoddy-looking tabs, and almost no styling. But, in
the interest of deliver early deliver often, and open sourcing this
project from even the first ugly start, here is the progress so far. 

# How to use it

To use the VWP, you have to run it locally, for now. That means you need to 
have flask installed, and you need the virtual watershed adaptors
(VWA). The VWA are included as a git submodule in the vwplatform repo.
So after cloning this repository, get the VWA by running

```bash
$ git submodule update --init --recursive
```

Then to launch view the web app first launch it

```bash
$ python models.py runserver
```

Then view it at `localhost:5000` in your web browser.
