# GardenPi

## Installation

### Install poetry

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
```

### Install dependencies

Install BLAS (see [here](https://numpy.org/devdocs/user/troubleshooting-importerror.html))

```
sudo apt-get install libatlas-base-dev
```

Install pip dependencies

```
poetry install
```

### Copy systemd unit file

```
mkdir -p ~/.config/systemd/user
cp gardenpi.service ~/.config/systemd/user
```

### Start systemd service

```
systemctl --user start gardenpi.service
```

### Enable service on reboot

```
systemctl --user enable gardenpi.service
```