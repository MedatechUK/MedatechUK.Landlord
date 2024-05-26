move M:\python\MedatechUK.Landlord\package\dist\*.* M:\python\MedatechUK.Landlord\package\old
m:
CD m:\python\MedatechUK.Landlord\package
py -m build
twine upload dist/*
cd ..