---
layout: post
title:  Install Different Versions of Python from Source
date:   2020-08-01 22:01:01 +0600
categories: published fedora linux install python development
---
Python 3.8 comes as a default with Fedora 32. However, sometimes you may wish to install other versions for development and test purposes. In this post, I will show you how to install Python 3.7 and 3.6 on Fedora 32.

## Install Prerequisites

#### Install python development dependencies

```bash
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel openssl-devel zlib-devel bzip2-devel sqlite-devel libffi-devel
```

#### Download source from official FTP site

Visit [https://www.python.org/ftp/python](https://www.python.org/ftp/python/) to download the `.tgz` file for the Python version you want to install.


## Install Python 3.7

#### Download and extract source archive

```bash
wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tgz
tar xzf Python-3.7.7.tgz Python-3.7.7/
```

#### Configure with all optimizations

```bash
cd Python-3.7.7/
./configure --enable-optimizations --with-ensurepip=install
```

#### Do not touch system default python

```bash
sudo make altinstall
```

#### Cleanup

```bash
cd .. && sudo rm -rf Python-3.7.7/
```


## Install Python 3.6

#### Download and extract source archive

```bash
wget https://www.python.org/ftp/python/3.6.10/Python-3.6.10.tgz
tar xzf Python-3.6.10.tgz Python-3.6.10/
```

#### Configure with all optimizations

```bash
cd Python-3.6.10/
./configure --enable-optimizations --with-ensurepip=install
```

#### Do not touch system default python

```bash
sudo make altinstall
```

#### Cleanup

```bash
cd .. && sudo rm -rf Python-3.6.10/
```


## Other versions of Python 3

You can easily install other versions of Python 3 by following similar steps as above.


## Note

You can remove the `.tgz` files, or keep them for future reinstalls. You will need to rebuild and reinstall respective Python versions again if you install new libraries that python should interact with.
