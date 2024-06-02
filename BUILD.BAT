DEL .\package\src\MedatechUK\Landlord\LandlordIcons.py
pyside6-rcc .\res\Landlord.qrc -o .\package\src\MedatechUK\Landlord\Icons.py
copy .\package\src\MedatechUK\Landlord\Icons.py "C:\Program Files\Python312\Lib\site-packages\MedatechUK\Landlord" /y

pyuic6 -x Landlord.ui -o "C:\Program Files\Python312\Lib\site-packages\MedatechUK\Landlord\qtoutput.py"

copy readme.md "./package/readme.md" /y

XCOPY "C:\Program Files\Python312\Lib\site-packages\MedatechUK\Landlord\*.*" ".\src\MedatechUK\Landlord\" /s /y
move .\package\dist\*.* .\package\old
cd package
py -m build
twine upload dist/*
cd ..