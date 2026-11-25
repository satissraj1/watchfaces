"""Tiny Watch Face Format (WFF) toolkit: XML helpers, hand/asset rendering, APK build."""
import math, os, re, shutil, subprocess
from PIL import Image, ImageDraw, ImageFilter

W = H = 450
CX = CY = 225
ROOT = os.path.dirname(os.path.abspath(__file__))
SDK = os.path.expanduser("~/Library/Android/sdk")
BT = os.path.join(SDK, "build-tools", "36.0.0")
ANDROID_JAR = os.path.join(SDK, "platforms", "android-36", "android.jar")
SS = 4  # supersampling


def polar(r, deg, cx=CX, cy=CY):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def slug(t):
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")


# ---------------------------------------------------------------- XML shapes
def stroke(color, th, cap="ROUND"):
    return f'<Stroke color="{color}" thickness="{f(th)}" cap="{cap}"/>'


def fill(color):
    return f'<Fill color="{color}"/>'


def line(x1, y1, x2, y2, color, th, cap="ROUND"):
    return f'<Line startX="{f(x1)}" startY="{f(y1)}" endX="{f(x2)}" endY="{f(y2)}">{stroke(color, th, cap)}</Line>'


def radial_line(r1, r2, deg, color, th, cap="ROUND", cx=CX, cy=CY):
    x1, y1 = polar(r1, deg, cx, cy)
    x2, y2 = polar(r2, deg, cx, cy)
    return line(x1, y1, x2, y2, color, th, cap)


def circle(r, color=None, stroke_color=None, th=2, cx=CX, cy=CY, inner=""):
    body = (fill(color) if color else "") + (stroke(stroke_color, th) if stroke_color else "") + inner
    return f'<Ellipse x="{f(cx - r)}" y="{f(cy - r)}" width="{f(2 * r)}" height="{f(2 * r)}">{body}</Ellipse>'


def radial_fill(r, colors, positions, cx=CX, cy=CY):
    return (f'<Ellipse x="{f(cx - r)}" y="{f(cy - r)}" width="{f(2 * r)}" height="{f(2 * r)}">'
            f'<Fill color="#FFFFFFFF"><RadialGradient centerX="{f(cx)}" centerY="{f(cy)}" radius="{f(r)}" '
            f'colors="{" ".join(colors)}" positions="{" ".join(f(p) for p in positions)}"/></Fill></Ellipse>')


def rrect(x, y, w, h, r, color=None, stroke_color=None, th=2):
    body = (fill(color) if color else "") + (stroke(stroke_color, th) if stroke_color else "")
    return f'<RoundRectangle x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" cornerRadiusX="{f(r)}" cornerRadiusY="{f(r)}">{body}</RoundRectangle>'


def arc(r, start, end, color, th, cx=CX, cy=CY, cap="ROUND", inner=""):
    return (f'<Arc centerX="{f(cx)}" centerY="{f(cy)}" width="{f(2 * r)}" height="{f(2 * r)}" '
            f'startAngle="{f(start)}" endAngle="{f(end)}">{stroke(color, th, cap)}{inner}</Arc>')


def draw(*shapes, x=0, y=0, w=W, h=H, extra="", name=None):
    n = f' name="{name}"' if name else ""
    return f'<PartDraw{n} x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}">{extra}{"".join(shapes)}</PartDraw>'


def group(*children, name="g", alpha=255, extra="", x=0, y=0, w=W, h=H):
    return f'<Group name="{name}" x="{x}" y="{y}" width="{w}" height="{h}" alpha="{alpha}">{extra}{"".join(children)}</Group>'


def active(*children):
    """Visible in interactive mode only."""
    return group(*children, name="active", extra='<Variant mode="AMBIENT" target="alpha" value="0" duration="0.55" interpolation="EASE_OUT"/>')


def ambient(*children):
    """Visible in ambient (AOD) only."""
    return group(*children, name="ambient", alpha=0, extra='<Variant mode="AMBIENT" target="alpha" value="255" startOffset="0.35" duration="0.65" interpolation="EASE_OUT"/>')


def font(family, size, color, content, letter=None):
    ls = f' letterSpacing="{f(letter)}"' if letter is not None else ""
    return f'<Font family="{family}" size="{f(size)}" color="{color}"{ls}>{content}</Font>'


def tpl(fmt, *exprs):
    return "<Template>" + fmt + "".join(f'<Parameter expression="{e}"/>' for e in exprs) + "</Template>"


def text(x, y, w, h, *fonts_, align="CENTER", extra=""):
    # runtime misplaces PartText with fractional coords -> always whole pixels
    x, y, w, h = (int(round(v)) for v in (x, y, w, h))
    return (f'<PartText x="{x}" y="{y}" width="{w}" height="{h}">{extra}'
            f'<Text align="{align}">{"".join(fonts_)}</Text></PartText>')


def list_scene(cid, options):
    """options: list of xml (index = option id)."""
    return f'<ListConfiguration id="{cid}">' + "".join(
        f'<ListOption id="{i}">{o}</ListOption>' for i, o in enumerate(options)) + "</ListConfiguration>"


def bool_scene(cid, on, off=""):
    s = f'<BooleanConfiguration id="{cid}"><BooleanOption id="TRUE">{on}</BooleanOption>'
    if off:
        s += f'<BooleanOption id="FALSE">{off}</BooleanOption>'
    return s + "</BooleanConfiguration>"


def C(cid, i=0):
    return f"[CONFIGURATION.{cid}.{i}]"


def hand(tag, res, img, px, py, cx=CX, cy=CY, tint=None, inner=""):
    """img: PIL image; (px,py) pivot in image pixels. Places pivot at (cx,cy) of the AnalogClock box."""
    w, h = img.size
    if px != int(px) or py != int(py):
        raise ValueError(f"{res}: hand must have even size and integer pivot ({w}x{h}, {px},{py})")
    t = f' tintColor="{tint}"' if tint else ""
    return (f'<{tag} resource="{res}" x="{f(cx - px)}" y="{f(cy - py)}" width="{w}" height="{h}" '
            f'pivotX="{f(px / w)}" pivotY="{f(py / h)}"{t}>{inner}</{tag}>')


def clock(*hands, x=0, y=0, w=W, h=H):
    return f'<AnalogClock x="{x}" y="{y}" width="{w}" height="{h}">{"".join(hands)}</AnalogClock>'


SWEEP = '<Sweep frequency="15"/>'


# ---------------------------------------------------------------- hand images (white, tinted at runtime)
def _canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def _down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def bar_hand(width, length, tail=0, pad=2, blur=0, round_=True, cap_r=0):
    """Vertical bar pointing up. Returns (img, pivot_x, pivot_y)."""
    pad = max(pad, int(blur * 3))
    w = int(math.ceil(max(width, cap_r * 2))) + 2 * pad
    w += w % 2
    h = int(math.ceil(length + tail)) + 2 * pad
    im = _canvas(w, h)
    d = ImageDraw.Draw(im)
    x0 = (w / 2 - width / 2) * SS
    x1 = (w / 2 + width / 2) * SS
    y0 = pad * SS
    y1 = (pad + length + tail) * SS
    rad = width / 2 * SS if round_ else 0
    d.rounded_rectangle([x0, y0, x1, y1], radius=rad, fill=(255, 255, 255, 255))
    py = pad + length
    if cap_r:
        d.ellipse([(w / 2 - cap_r) * SS, (py - cap_r) * SS, (w / 2 + cap_r) * SS, (py + cap_r) * SS], fill=(255, 255, 255, 255))
    im = _down(im, w, h)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im, w / 2, py


def dot_hand(orbit, r, blur=0, ring=0):
    """Dot at distance `orbit` above pivot. ring>0 -> hollow ring of that stroke."""
    pad = 2 + int(blur * 3)
    w = int(math.ceil(2 * r)) + 2 * pad
    w += w % 2
    h = int(math.ceil(orbit + r)) + pad + 2
    im = _canvas(w, h)
    d = ImageDraw.Draw(im)
    cx, cy = w / 2, h - orbit
    box = [(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS]
    if ring:
        d.ellipse(box, outline=(255, 255, 255, 255), width=int(ring * SS))
    else:
        d.ellipse(box, fill=(255, 255, 255, 255))
    im = _down(im, w, h)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im, w / 2, h


# ---------------------------------------------------------------- face + build
class Face:
    def __init__(self, key, label, version=4):
        self.key, self.label, self.version = key, label, version
        self.strings = {"app_name": label}
        self.images = {}
        self.fonts = set()
        self.cfg = []
        self.scene = []
        self.preview_time = "10:08:36"
        self.clock_type = "ANALOG"

    def s(self, t):
        k = "s_" + slug(t)
        self.strings[k] = t
        return k

    def img(self, name, im):
        self.images[name] = im
        return name

    def font(self, name):
        self.fonts.add(name)
        return name

    @staticmethod
    def _ovr(cid, default):
        """OVR="theme=1,ticks=2" overrides defaults (review renders only)."""
        for kv in filter(None, os.environ.get("OVR", "").split(",")):
            k, v = kv.split("=")
            if k == cid:
                return v
        return default

    def color_cfg(self, cid, label, options, default=0):
        if cid == "theme":  # dark mode by default
            names = [n for n, _ in options]
            default = next((i for i, n in enumerate(names) if n in ("Dark", "Dusk", "Charcoal")), default)
        if cid == "theme" and os.environ.get("THEME_IDX"):
            default = int(os.environ["THEME_IDX"])
        opts = "".join(f'<ColorOption id="{i}" displayName="{self.s(n)}" colors="{" ".join(c)}"/>'
                       for i, (n, c) in enumerate(options))
        default = self._ovr(cid, default)
        self.cfg.append(f'<ColorConfiguration id="{cid}" displayName="{self.s(label)}" defaultValue="{default}">{opts}</ColorConfiguration>')

    def list_cfg(self, cid, label, options, default=0):
        opts = "".join(f'<ListOption id="{i}" displayName="{self.s(n)}"/>' for i, n in enumerate(options))
        default = self._ovr(cid, default)
        self.cfg.append(f'<ListConfiguration id="{cid}" displayName="{self.s(label)}" defaultValue="{default}">{opts}</ListConfiguration>')

    def bool_cfg(self, cid, label, default=True):
        default = self._ovr(cid, "TRUE" if default else "FALSE")
        self.cfg.append(f'<BooleanConfiguration id="{cid}" displayName="{self.s(label)}" defaultValue="{default}"/>')

    def add(self, *xml):
        self.scene.extend(xml)

    def xml(self):
        return ('<?xml version="1.0" encoding="utf-8"?>\n'
                f'<WatchFace width="{W}" height="{H}" clipShape="CIRCLE">'
                f'<Metadata key="CLOCK_TYPE" value="{self.clock_type}"/>'
                f'<Metadata key="PREVIEW_TIME" value="{self.preview_time}"/>'
                f'<UserConfigurations>{"".join(self.cfg)}</UserConfigurations>'
                f'<Scene backgroundColor="#FF000000">{"".join(self.scene)}</Scene></WatchFace>\n')

    # -------------------------------------------------------------- build
    def build(self, out_dir, preview=None):
        pkg = f"com.studio.wff.{self.key}"
        if os.environ.get("REVIEW"):  # throwaway review copy, never touches the user's installed face
            pkg = f"com.studio.wff.review.{self.key}"
            self.strings["app_name"] = self.label + " (review)"
        d = os.path.join(ROOT, "build", self.key)
        shutil.rmtree(d, ignore_errors=True)
        res = os.path.join(d, "res")
        for sub in ("raw", "xml", "values", "drawable-nodpi", "font"):
            os.makedirs(os.path.join(res, sub), exist_ok=True)
        with open(os.path.join(res, "raw", "watchface.xml"), "w") as fh:
            fh.write(self.xml())
        with open(os.path.join(res, "xml", "watch_face_info.xml"), "w") as fh:
            fh.write('<?xml version="1.0" encoding="utf-8"?>\n<WatchFaceInfo>'
                     '<Preview value="@drawable/preview"/>'
                     '<Category value="CATEGORY_EMPTY"/>'
                     '<AvailableInRetail value="true"/>'
                     '<MultipleInstancesAllowed value="true"/>'
                     '<Editable value="true"/></WatchFaceInfo>\n')
        with open(os.path.join(res, "values", "strings.xml"), "w") as fh:
            esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace("'", "\\'")
            fh.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>' +
                     "".join(f'<string name="{k}">{esc(v)}</string>' for k, v in self.strings.items()) + "</resources>\n")
        for name, im in self.images.items():
            im.save(os.path.join(res, "drawable-nodpi", name + ".png"))
        prev_src = preview or os.path.join(ROOT, "previews", self.key + ".png")
        if os.path.exists(prev_src):
            Image.open(prev_src).convert("RGBA").resize((300, 300), Image.LANCZOS).save(os.path.join(res, "drawable-nodpi", "preview.png"))
        else:
            Image.new("RGBA", (300, 300), (40, 40, 40, 255)).save(os.path.join(res, "drawable-nodpi", "preview.png"))
        for fn in self.fonts:
            shutil.copy(os.path.join(ROOT, "fonts", fn + ".ttf"), os.path.join(res, "font", fn + ".ttf"))
        if not self.fonts:
            os.rmdir(os.path.join(res, "font"))
        with open(os.path.join(d, "AndroidManifest.xml"), "w") as fh:
            fh.write(f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{pkg}" android:versionCode="1" android:versionName="1.0">
  <uses-feature android:name="android.hardware.type.watch"/>
  <application android:label="@string/app_name" android:hasCode="false">
    <meta-data android:name="com.google.android.wearable.standalone" android:value="true"/>
    <property android:name="com.google.wear.watchface.format.version" android:value="{self.version}"/>
    <property android:name="com.google.wear.watchface.format.publisher" android:value="studio"/>
  </application>
</manifest>
''')
        aapt2 = os.path.join(BT, "aapt2")
        run([aapt2, "compile", "--dir", res, "-o", os.path.join(d, "res.zip")])
        run([aapt2, "link", "-o", os.path.join(d, "u.apk"), "-I", ANDROID_JAR, "--manifest",
             os.path.join(d, "AndroidManifest.xml"), "--min-sdk-version", "33", "--target-sdk-version", "34",
             os.path.join(d, "res.zip")])
        run([os.path.join(BT, "zipalign"), "-f", "4", os.path.join(d, "u.apk"), os.path.join(d, "a.apk")])
        os.makedirs(out_dir, exist_ok=True)
        apk = os.path.join(out_dir, f"{self.key}{'_review' if os.environ.get('REVIEW') else ''}.apk")
        run([os.path.join(BT, "apksigner"), "sign", *signing_args(), "--out", apk, os.path.join(d, "a.apk")])
        return pkg, apk


RELEASE_PROPS = os.path.expanduser(os.environ.get("WFF_RELEASE_PROPS", "~/.android/watchfaces-release.properties"))


def signing_args():
    """Release key when RELEASE=1 (key + password live outside the repo), else the debug key."""
    if os.environ.get("RELEASE"):
        if not os.path.exists(RELEASE_PROPS):
            raise SystemExit(f"RELEASE=1 but {RELEASE_PROPS} not found")
        p = dict(l.strip().split("=", 1) for l in open(RELEASE_PROPS) if "=" in l)
        pw = f"pass:{p['password']}"
        return ["--ks", os.path.expanduser(p["storeFile"]), "--ks-key-alias", p["alias"], "--ks-pass", pw, "--key-pass", pw]
    return ["--ks", os.path.expanduser("~/.android/debug.keystore"), "--ks-key-alias", "androiddebugkey",
            "--ks-pass", "pass:android", "--key-pass", "pass:android"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        shown = ["pass:***" if str(c).startswith("pass:") else str(c) for c in cmd]
        raise SystemExit(f"FAILED: {' '.join(shown)}\n{r.stdout}\n{r.stderr}")
