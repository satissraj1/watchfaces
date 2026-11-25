import sys
from faces import FACES
names = sys.argv[1:] or list(FACES)
for n in names:
    F = FACES[n]()
    pkg, apk = F.build("out")
    print(pkg, apk)
