
# Generate wheel file

```commandline
python setup.py sdist bdist_wheel
```

# Test Install Locally

```commandline
python -m pip install .\dist\rr_inject-0.1.0-py3-none-any.whl --forc
```

# Publish to PyPi 
```commandline
twine upload dist/*
```