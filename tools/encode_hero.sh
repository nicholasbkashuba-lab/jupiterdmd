#!/usr/bin/env bash
# Reproducible encode of the Jupiter Inlet hero loop, posters, strip stills and share card.
#
# Usage:  tools/encode_hero.sh /path/to/inlet-1440p.mp4 [work_dir]
#
# Source: 2560x1440 H.264 drone footage, ~18.4 s, 24000/1001 fps.
# Needs:  ffmpeg with libx264 + libsvtav1, ffprobe, python3 with Pillow >= 11 (AVIF + WebP).
#
# Outputs (relative to the repo root):
#   assets/video/inlet-1080.mp4   H.264 High 1920x1080  <= 5.0 MB
#   assets/video/inlet-720.mp4    H.264 High 1280x720   <= 2.5 MB
#   assets/video/inlet-1080.webm  AV1 (SVT-AV1) 1920x1080 <= 4.0 MB
#   assets/video/inlet-portrait.mp4   H.264 High 720x960 (3:4 crop, same window as the phone poster) <= 2.0 MB
#   assets/video/inlet-portrait.webm  AV1 720x960 <= 1.6 MB
#   assets/img/hero/inlet-poster-{1920,1280}.{avif,webp,jpg}
#   assets/img/hero/inlet-poster-portrait-{720,1080}.{avif,webp,jpg}
#   assets/img/strip/<slug>-{480,960}.{avif,webp,jpg} + manifest.json
#   assets/img/og-base.jpg (1200x630)
set -euo pipefail

SRC="${1:?usage: $0 /path/to/source.mp4 [work_dir]}"
SRC="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${2:-$(mktemp -d)}"
mkdir -p "$WORK"
VID="$ROOT/assets/video"; HERO="$ROOT/assets/img/hero"; STRIP="$ROOT/assets/img/strip"
mkdir -p "$VID" "$HERO" "$STRIP"

FF="ffmpeg -hide_banner -loglevel error -y"
FPS="24000/1001"
XF=24                      # crossfade length in frames (24 frames = 1.001 s)
GRADE="${GRADE:-null}"     # no grade: the footage as shot (ffmpeg "null" passes frames through untouched)
TAGS="-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv"

# ---------------------------------------------------------------- 1. seamless loop master
# Count frames after CFR normalisation.
N=$($FF -i "$SRC" -an -vf "fps=$FPS" -f framemd5 - 2>/dev/null | grep -vc '^#')
echo "source frames at CFR: $N"
A0=$XF; A1=$((N - XF))      # body:   frames [XF, N-XF)
B0=$((N - XF)); B1=$N       # tail:   frames [N-XF, N)   fades out ...
C0=0; C1=$XF                # head:   frames [0, XF)     ... into the head
XFD=$(python3 -c "print(f'{$XF*1001/24000:.6f}')")

if [ ! -s "$WORK/master.mkv" ]; then
# master = concat( body, xfade(tail -> head) ); length N-XF frames.
# Lossless FFV1 intermediate at full 2560x1440 so every rendition / poster comes from the same pixels.
$FF -i "$SRC" -an -filter_complex "\
[0:v]fps=$FPS,$GRADE,format=yuv420p,split=3[s0][s1][s2];\
[s0]trim=start_frame=$A0:end_frame=$A1,setpts=PTS-STARTPTS[body];\
[s1]trim=start_frame=$B0:end_frame=$B1,setpts=PTS-STARTPTS[tail];\
[s2]trim=start_frame=$C0:end_frame=$C1,setpts=PTS-STARTPTS[head];\
[tail][head]xfade=transition=fade:duration=$XFD:offset=0,trim=end_frame=$XF[seam];\
[body][seam]concat=n=2:v=1:a=0,fps=$FPS[out]" \
  -map "[out]" -c:v ffv1 -level 3 -pix_fmt yuv420p $TAGS "$WORK/master.mkv"
fi

# ---------------------------------------------------------------- 2. renditions
# CRF search: encode at a starting CRF, then move CRF along a log model of size vs CRF
# (x264: ~6 CRF per halving of size; SVT-AV1: ~8) until the file lands in 92-100 % of budget.
# The lowest CRF that fits is kept. Every attempt is printed so the chosen value is on record.
SCALE="flags=lanczos:in_color_matrix=bt709:out_color_matrix=bt709"
enc () { # $1 kind $2 w $3 h $4 crf $5 out
  if [ "$1" = x264 ]; then
    $FF -i "$WORK/master.mkv" -an -vf "${PRE:+$PRE,}scale=$2:$3:$SCALE,format=yuv420p" \
      -c:v libx264 -preset veryslow -profile:v high -crf "$4" -g 48 -keyint_min 48 -sc_threshold 0 \
      -pix_fmt yuv420p $TAGS -movflags +faststart "$5"
  else
    $FF -i "$WORK/master.mkv" -an -vf "${PRE:+$PRE,}scale=$2:$3:$SCALE,format=yuv420p" \
      -c:v libsvtav1 -preset 4 -crf "$4" -g 48 -svtav1-params tune=0 \
      -pix_fmt yuv420p $TAGS "$5"
  fi
}
fit () { # $1 kind $2 w $3 h $4 out $5 budget_bytes $6 start_crf
  local kind=$1 out=$4 budget=$5 crf=$6 ext="${4##*.}" best="" tried=" " sz next
  for _ in 1 2 3 4 5 6; do
    enc "$kind" "$2" "$3" "$crf" "$WORK/try-$crf.$ext"
    sz=$(stat -c %s "$WORK/try-$crf.$ext"); tried="$tried$crf "
    echo "  $(basename "$out") crf=$crf -> $sz bytes (budget $budget)"
    if [ "$sz" -le "$budget" ]; then
      if [ -z "$best" ] || python3 -c "import sys; sys.exit(0 if $crf < $best else 1)"; then best=$crf; fi
      [ "$sz" -ge $((budget * 92 / 100)) ] && break
    fi
    next=$(python3 -c "
import math
k = 6.0 if '$kind' == 'x264' else 8.0
step = k * math.log2($sz / (0.96 * $budget))
c = $crf + step
c = round(c * 2) / 2 if '$kind' == 'x264' else round(c)
if c == $crf: c = $crf + (0.5 if '$kind' == 'x264' else 1) * (1 if $sz > $budget else -1)
print(int(c) if float(c).is_integer() else c)")
    case "$tried" in *" $next "*) break;; esac
    [ -n "$best" ] && python3 -c "import sys; sys.exit(0 if $next >= $best else 1)" && break
    crf=$next
  done
  [ -n "$best" ] || { echo "no CRF fit $out" >&2; exit 1; }
  cp "$WORK/try-$best.$ext" "$out"; rm -f "$WORK"/try-*."$ext"
  echo "  -> $(basename "$out"): crf $best, $(stat -c %s "$out") bytes"
}
if [ -z "${SKIP_VIDEO:-}" ]; then
fit x264 1920 1080 "$VID/inlet-1080.mp4"  5000000 ${CRF1080:-31}
fit x264 1280 720  "$VID/inlet-720.mp4"   2500000 ${CRF720:-30.5}
fit av1  1920 1080 "$VID/inlet-1080.webm" 4000000 ${CRFAV1:-46}
fi
# Phones: a 3:4 portrait window on the inlet mouth (x=1160, same as the portrait poster) so the
# video fades in over its own first frame without the framing jumping.
if [ -z "${SKIP_VIDEO:-}" ] || [ -n "${PORTRAIT_ONLY:-}" ]; then
PRE="crop=1080:1440:${PORTRAIT_X:-1160}:0" fit x264 720 960 "$VID/inlet-portrait.mp4"  2000000 ${CRFPM:-28}
PRE="crop=1080:1440:${PORTRAIT_X:-1160}:0" fit av1  720 960 "$VID/inlet-portrait.webm" 1600000 ${CRFPA:-44}
fi
[ -n "${PORTRAIT_ONLY:-}" ] && exit 0

# ---------------------------------------------------------------- 3. frame one of the loop -> RGB PNG
YUV2RGB="scale=in_color_matrix=bt709:in_range=tv:out_range=pc:flags=lanczos+accurate_rnd+full_chroma_int,format=rgb24"
$FF -i "$WORK/master.mkv" -vf "select=eq(n\,0),$YUV2RGB" -frames:v 1 "$WORK/frame1.png"

# ---------------------------------------------------------------- 4. strip stills + share card (from source, same grade)
# slug|t(s)|crop w:h:x:y (source px, 2560x1440)|aspect
STILLS=(
  "jupiter-coastline-beach-surf|3.0|1080:720:1480:330|3:2"
  "jupiter-inlet-jetty-tip-waves|4.0|864:1080:1240:360|4:5"
  "jupiter-inlet-beach-wave-curve|6.0|1350:900:0:540|3:2"
  "jupiter-inlet-channel-between-jetties|9.0|1080:1350:1000:90|4:5"
  "jupiter-inlet-shoreline-trees-lagoon|12.0|1200:800:0:360|3:2"
  "jupiter-inlet-waterfront-homes|15.0|960:1200:1600:240|4:5"
  "loxahatchee-river-sun-glint|18.0|1080:1350:680:90|4:5"
  "jupiter-sunset-sky-river-bend|6.5|1080:720:200:0|3:2"
)
for s in "${STILLS[@]}"; do
  IFS='|' read -r slug t crop asp <<<"$s"
  $FF -ss "$t" -i "$SRC" -vf "$GRADE,crop=$crop,$YUV2RGB" -frames:v 1 "$WORK/strip-$slug.png"
done
$FF -ss 14.0 -i "$SRC" -vf "$GRADE,crop=2048:1075:256:0,$YUV2RGB" -frames:v 1 "$WORK/og.png"

# ---------------------------------------------------------------- 5. stills -> avif/webp/jpg under budget (Pillow)
STILLS_SPEC="$(printf '%s\n' "${STILLS[@]}")" python3 - "$WORK" "$ROOT" <<'PY'
import io, json, os, sys
from PIL import Image
work, root = sys.argv[1], sys.argv[2]
hero, strip = f"{root}/assets/img/hero", f"{root}/assets/img/strip"

def save(img, path, budget_kb):
    """Encode with the highest quality that fits the budget; no EXIF/ICC/XMP written."""
    fmt = path.rsplit(".", 1)[1]
    img = img.convert("RGB")
    for q in range(90, 29, -2):
        buf = io.BytesIO()
        if fmt == "jpg":
            img.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling="4:2:0")
        elif fmt == "webp":
            img.save(buf, "WEBP", quality=q, method=6)
        else:
            img.save(buf, "AVIF", quality=q - 20, speed=4, subsampling="4:2:0")  # Pillow AVIF q scale runs lower
        if buf.tell() <= budget_kb * 1000:  # decimal KB, strictest reading
            break
    open(path, "wb").write(buf.getvalue())
    print(f"  {os.path.basename(path):48s} {buf.tell()/1000:7.1f} KB (q={q if fmt!='avif' else q-20}, budget {budget_kb})")

def resize(img, w):
    h = round(img.height * w / img.width)
    return img if img.width == w else img.resize((w, h), Image.LANCZOS)

f1 = Image.open(f"{work}/frame1.png")            # frame one of the final loop, 2560x1440
B = {  # (avif, webp, jpg) budgets in KB
  1920: (140, 200, 260), 1280: (80, 120, 160),
  "p1080": (100, 150, 200), "p720": (55, 80, 110),
}
for w in (1920, 1280):
    im = resize(f1, w)
    for ext, b in zip(("avif", "webp", "jpg"), B[w]):
        save(im, f"{hero}/inlet-poster-{w}.{ext}", b)

# portrait poster: 1080x1440 window (3:4) on the inlet mouth - both jetty tips, channel, north beach
PX = int(os.environ.get("PORTRAIT_X", "1160"))
pt = f1.crop((PX, 0, PX + 1080, 1440))
for w, key in ((1080, "p1080"), (720, "p720")):
    im = resize(pt, w)
    for ext, b in zip(("avif", "webp", "jpg"), B[key]):
        save(im, f"{hero}/inlet-poster-portrait-{w}.{ext}", b)

ALTS = {
  "jupiter-coastline-beach-surf": "Beach and breaking surf running north from Jupiter Inlet toward distant high-rise buildings, seen from above at sunset",
  "jupiter-inlet-jetty-tip-waves": "The curved end of a rock jetty at Jupiter Inlet with waves wrapping around it, seen from above",
  "jupiter-inlet-beach-wave-curve": "A curving sandy beach and low waves inside the Jupiter Inlet jetty, with trees and shrubs behind, at dusk",
  "jupiter-inlet-channel-between-jetties": "The Jupiter Inlet channel running between two rock jetties toward the river and a sunset sky",
  "jupiter-inlet-shoreline-trees-lagoon": "Trees, footpaths and a small lagoon on the shore beside Jupiter Inlet, seen from above in evening light",
  "jupiter-inlet-waterfront-homes": "Waterfront homes, a sandy beach and a rock jetty on the north side of Jupiter Inlet at dusk",
  "loxahatchee-river-sun-glint": "The setting sun reflecting off the water as the Loxahatchee River runs out through Jupiter Inlet",
  "jupiter-sunset-sky-river-bend": "A sunset sky over the river, bridges and wooded shoreline west of Jupiter Inlet, with the red Jupiter Inlet Lighthouse in the distance",
}
manifest = []
for line in os.environ["STILLS_SPEC"].splitlines():
    slug, t, crop, asp = line.split("|")
    src = Image.open(f"{work}/strip-{slug}.png")
    for w, b in ((480, (30, 40, 55)), (960, (80, 110, 160))):
        im = resize(src, w)
        for ext, kb in zip(("avif", "webp", "jpg"), b):
            save(im, f"{strip}/{slug}-{w}.{ext}", kb)
    im960 = resize(src, 960)
    manifest.append({"slug": slug, "w": im960.width, "h": im960.height, "alt": ALTS[slug], "t": float(t)})
json.dump(manifest, open(f"{strip}/manifest.json", "w"), indent=2)
open(f"{strip}/manifest.json", "a").write("\n")

og = Image.open(f"{work}/og.png").resize((1200, 630), Image.LANCZOS)
save(og, f"{root}/assets/img/og-base.jpg", 200)
PY
echo "done. work dir: $WORK"
