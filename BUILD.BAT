CD package
move .\dist\*.* .\old
DEL .\src\MedatechUK\Landlord\LandlordIcons.py
pyside6-rcc ..\res\Landlord.qrc -o .\src\MedatechUK\Landlord\LandlordIcons.py
py -m build
twine upload dist/*
cd ..