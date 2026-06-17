# Our Paper, in Plain Language — a Guide for Writing It

Hi! This is a friendly walkthrough of what our paper is actually about, so you can
write it confidently. The paper has some scary-looking math, but you do **not** need
it to understand (or explain) the work. I'll use plain words first, then quietly show
you which technical term each plain word maps to — but the technical names are *not*
the point. The ideas are.

---

## 1. The one-sentence version

> We made a small, camera-only depth-estimation model work noticeably better in
> citrus orchards — **without using any depth labels to train it, and without making
> the model any heavier or slower to run.**

That's the whole paper. Everything else is *how* and *how do we know it worked*.

---

## 2. The problem (set the stage)

- A farm robot wants to know **how far away** things are (trees, ground, obstacles)
  using just a **single cheap camera** — no LiDAR, no stereo, no expensive sensors.
- A model called **Lite-Mono** does this: feed it one photo, it outputs a depth map.
  It's **lightweight** (tiny enough for a small robot) and it's **self-supervised**,
  meaning it learns from ordinary video **without anyone labelling the true depths**.
- The catch: models like this are usually trained and tested on **city driving**
  footage. Orchards are very different — dense leaves, repeating textures, big open
  dirt patches, sky with no useful info. So the model does a mediocre job there.

**Our goal:** make it better *for orchards*, while keeping two promises:
1. **No cheating with labels** — training stays label-free (real depth/LiDAR is used
   *only* to score results at the end, never to train).
2. **No heavier model** — at run time it's the exact same single-camera Lite-Mono.

---

## 3. Our main idea — the selling point ⭐

This is the part to emphasize. It's simple and a little clever.

### The "self-teacher"
Normally if you want a model to improve, you'd have a smarter *teacher* model correct
it. But we're not allowed an external teacher (that would break our label-free
promise). So we made the model **teach itself** — using a calmer version of itself.

**The analogy:** imagine a student studying the orchard every day. On any single day
the student is a bit jumpy and inconsistent. So we keep a **slow running-average copy**
of the student — like the student's "calm, experienced self" that smooths out the
daily ups and downs. That calm average copy has genuinely learned the orchard, so it
makes a **great teacher** for the day-to-day student.

That's the heart of the paper: a **teacher that is a slow average of the student
itself, and that has adapted to the orchard.** Crucially, this teacher only exists
*during training* — once training is done, we throw it away and ship the plain model.
So the robot pays **zero extra cost.**

> Plain word → paper word: "calm slow-average copy" = **EMA self-teacher**
> (EMA = exponential moving average). "In-domain" just means it learned the orchard.

### How the teacher coaches the student (two gentle nudges)
1. **"Match my distances."** The teacher tells the student what depth to predict. The
   clever bit: it compares **shapes of depth, ignoring the overall scale/brightness
   offset.** Think of it like comparing two drawings of the same hill regardless of how
   zoomed-in each one is. This is the nudge that moved our **main accuracy number** the
   most.
   > paper word: *scale-invariant (SI-log) depth term*.
2. **"Keep the overall layout sensible."** A second, softer nudge that protects the
   *relative* near-vs-far ordering, so the model doesn't get more accurate at the cost
   of looking broken.
   > paper word: *normalized structure anchor*.

### One honest detail (and it's actually a strength)
We also built "trust filters" so the student would only listen to the teacher on
**reliable** pixels. When we checked, those filters barely did anything (they kept
~88% of pixels — basically "trust almost everything"). So we say so plainly: **the
win came from the broad self-teaching, not from the filters.** Being honest about
this makes the paper more trustworthy, not less. (We note the filters deserve a proper
follow-up test.)

---

## 4. Why it's a big deal — the results (the numbers that sell)

Two scores reviewers care about (don't worry about the formulas):
- **abs_rel** = how wrong the depths are on average (a fraction). **Lower is better.**
- **a1** = the share of pixels predicted within 25% of the true depth. **Higher is better.**

| Model | abs_rel ↓ | a1 ↑ |
|---|---|---|
| Original Lite-Mono (the baseline) | 0.3836 | 0.4989 |
| Our previous attempt (S07) | 0.3840 | 0.6539 |
| **Our method (S10)** | **0.3080** | **0.6258** |

**The headline:** our method is the **first one in our whole project to clearly beat
the original model on the main error score** — about **20% lower error**, while *also*
being about **25% better** on the "within 25%" score than the original. And we
double-checked it on a fresh run and got the exact same numbers.

(Honest footnote: against our own previous attempt S07, we win big on error for a tiny
give-back on the a1 score — a good trade.)

**Why a reviewer should care:**
- It's **label-free, single-camera, lightweight, and unchanged at run time** → genuinely
  practical for cheap farm robots.
- The **self-teacher idea is a neat twist**: the teacher is an in-domain average of the
  model itself, not a big external model — so it stays pure and cheap.
- As far as we found, **nobody has shown label-free depth working in an orchard before**
  — it's open territory.

---

## 5. The honesty that makes the paper strong (not just hype)

Good papers admit limits — reviewers respect it, and we have a clean story here:
- **We improved the *numbers*, not the *looks*.** The depth pictures still struggle with
  sky/far trees and over-smooth the canopy. We show this openly.
- **We diagnosed *why* everything is hard:** all these models secretly lean on a
  shortcut — "lower in the image = closer" (a ground ramp). Our method mostly makes that
  ramp *better calibrated* rather than truly understanding tree shapes.
- **We report what didn't work.** We tried ~10 ideas (sharpening edges, extra
  consistency tricks, a crop-zoom trick that collapsed). These "failures" are a real
  contribution: they explain *why* the gentle self-teacher is the thing that finally
  worked. Reviewers love an honest map of the dead ends.
- **One dataset so far** (one citrus-farm sequence) — we say generalization is untested.

---

## 6. The five selling points (lift these straight into the intro)

1. **A new, simple idea:** an *in-domain self-teacher* (a slow average of the model)
   that coaches the model during training and then disappears.
2. **First clear win** over the original lightweight baseline on the main error metric,
   in this label-free orchard setting (~20% lower error).
3. **Free at run time:** inference is the unchanged, single-camera, lightweight model.
4. **Fully honest + reproducible:** we re-ran and matched results, and we openly report
   limits and a diagnosed failure mode.
5. **New territory:** first label-free depth study validated on an orchard.

---

## 7. Quick "jargon decoder" (so the paper's words don't scare you)

| In the paper you'll see… | It just means… |
|---|---|
| self-supervised / label-free | trains from video, no depth labels |
| monocular | one camera, one image |
| EMA self-teacher | a slow running-average copy of the model, used as a teacher |
| in-domain | it has learned the orchard (not generic city data) |
| distillation | the teacher passing its knowledge to the student |
| scale-invariant / SI-log term | "match the depth *shape*, ignore overall scale" |
| structure anchor | "keep near-vs-far ordering sensible" |
| reliability gates (DC/GC) | "only trust the teacher on dependable pixels" (turned out barely used) |
| abs_rel / a1 | average error (lower=better) / % within 25% (higher=better) |
| median scaling | a standard fairness step before scoring |

---

## 8. What each figure shows (handy when writing captions / text)

- **Method diagram** *(to be drawn in draw.io)* — the training setup: student + the
  slow self-teacher + the two nudges. The one figure still on our to-do list.
- **Validation-over-epochs graph** — our method (S10) steadily dropping below our
  previous best (S07) and below the baseline line, as training goes on.
- **Qualitative depth panels** (corridor = easy, clearing = hard) — RGB, the LiDAR
  "answer key," then Original/S07/S10 depth side by side. Shows they look similar →
  supports our honest "better numbers, similar looks" point.
- **Error-vs-distance** — where the error lives (near-range / open clearings are worst).
- **Ground-vs-vegetation split** — our gains come mostly from ground (labels are ~84%
  ground), so vegetation is now the harder remaining part.
- **Keep-ratio graph** — proof the trust-filters were near-inert (~88% kept).
- **S11 collapse** — the crop-zoom idea that failed (predicted a flat constant depth).

---

### Still on the human to-do list (just so you know)
- Draw the **method diagram** (we're continuing the previous draw.io diagram).
- Fill the **author block** (names, university, department).
- **Double-check the references** marked "UNVERIFIED" in the .bib (especially the
  CitrusFarm dataset citation).

That's everything. The story is: *a simple, honest, label-free self-teaching trick that
finally beats the baseline on a hard new domain, with no extra cost to run.* 🍊
