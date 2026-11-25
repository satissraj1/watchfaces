#!/bin/zsh
# usage: ./review.sh face "ovr" "ovr" ... -> shots/review/<face>.png sheet, using a throwaway review package
S=${WATCH:-adb-RFAT804QNKH-SaWRFz._adb-tls-connect._tcp}
f=$1; shift; i=0; names=(); mkdir -p shots/review
for o in "$@"; do
  REVIEW=1 OVR="$o" python3 build.py $f >/dev/null || { echo "build fail $f $o"; continue; }
  adb -s $S uninstall com.studio.wff.review.$f >/dev/null 2>&1
  adb -s $S install out/${f}_review.apk >/dev/null 2>&1 || echo "install fail $f"
  adb -s $S shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId com.studio.wff.review.$f >/dev/null
  adb -s $S shell input keyevent KEYCODE_WAKEUP; sleep 4
  adb -s $S exec-out screencap -p > shots/review/${f}_$i.png
  names+=(review/${f}_$i); i=$((i+1))
done
adb -s $S uninstall com.studio.wff.review.$f >/dev/null 2>&1
python3 sheet.py shots/review/${f}_sheet.png $names
echo "reviewed $f ($i variants)"
