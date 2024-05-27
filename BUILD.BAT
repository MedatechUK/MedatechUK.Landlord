CD package
move .\dist\*.* .\old
py -m build
twine upload dist/*
cd ..
pip uninstall MedatechUK.Landlord
pip install MedatechUK.Landlord==0.0.15