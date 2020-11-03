sudo python setup.py install
sudo pip install twine
sudo twine upload dist/*
sudo rm -rf namekox_core.egg-info build dist
