#!/bin/zsh
# usage: ./variants.sh face "ovr1" "ovr2" ...  -> shots/<face>_v<i>.png + sheet shots/<face>_variants.png
f=$1; shift; i=0; names=()
for o in "$@"; do
  OVR="$o" python3 build.py $f >/dev/null && ./shoot.sh $f >/dev/null && cp shots/$f.png shots/${f}_v$i.png
  names+=(${f}_v$i); i=$((i+1))
done
python3 sheet.py shots/${f}_variants.png $names
python3 build.py $f >/dev/null && ./shoot.sh $f >/dev/null   # restore default build on the watch
