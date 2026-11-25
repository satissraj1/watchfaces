#!/bin/zsh
# usage: ./push.sh face  -> rebuild, update in place (no uninstall, no face switching), screenshot
S=${WATCH:-adb-RFAT804QNKH-SaWRFz._adb-tls-connect._tcp}
n=$1
python3 build.py $n >/dev/null || exit 1
adb -s $S install -r out/$n.apk >/dev/null 2>&1 || echo "install fail"
adb -s $S shell input keyevent KEYCODE_WAKEUP
sleep 3
adb -s $S exec-out screencap -p > shots/$n.png
echo "pushed $n"
