#!/bin/zsh
# usage: ./shoot.sh face...  fresh install (no duplicate favorites, default config), activate, capture 3 frames
S=${WATCH:-adb-RFAT804QNKH-SaWRFz._adb-tls-connect._tcp}
mkdir -p shots
for n in "$@"; do
  adb -s $S uninstall com.studio.wff.$n >/dev/null 2>&1
  adb -s $S install out/$n.apk >/dev/null 2>&1 || echo "install fail $n"
  adb -s $S shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId com.studio.wff.$n >/dev/null
  adb -s $S shell input keyevent KEYCODE_WAKEUP; adb -s $S shell input keyevent KEYCODE_HOME
  sleep 4
  for k in 1 2 3; do adb -s $S exec-out screencap -p > shots/${n}_$k.png; done
  cp shots/${n}_1.png shots/$n.png
  echo "shot $n"
done
