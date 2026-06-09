---
name: Civly
description: Find federal regulations open for public comment and file a substantive comment that counts.
colors:
  ink: "#141413"
  ink-soft: "#6e6960"
  paper: "#faf9f5"
  muted: "#b0aea5"
  subtle: "#e8e6dc"
  terracotta: "#d97757"
  terracotta-deep: "#c4634a"
  blue: "#6a9bcc"
  olive: "#788c5d"
typography:
  display:
    fontFamily: "Poppins, Arial, sans-serif"
    fontSize: "3rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "normal"
  headline:
    fontFamily: "Poppins, Arial, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "normal"
  title:
    fontFamily: "Poppins, Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "normal"
  body:
    fontFamily: "Lora, Georgia, serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Poppins, Arial, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "normal"
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  full: "9999px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "32px"
components:
  button-primary:
    backgroundColor: "{colors.terracotta}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  button-primary-hover:
    backgroundColor: "{colors.terracotta-deep}"
    textColor: "{colors.paper}"
  button-primary-disabled:
    backgroundColor: "{colors.subtle}"
    textColor: "{colors.muted}"
  chip-filter:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.muted}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
  chip-filter-selected:
    backgroundColor: "{colors.terracotta}"
    textColor: "{colors.paper}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
  card-rule:
    backgroundColor: "{colors.subtle}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "16px"
  input-text:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
---

# Design System: Civly

## 1. Overview

**Creative North Star: "The Public Reading Room"**

Civly is a calm, literate place where an ordinary person can walk in off the street and engage with the federal record on equal footing. The serif body type (Lora) reads like a printed page, a Federal Register notice rendered human; the warm off-white field feels like good paper under a reading lamp, not a government form under fluorescent light. Civly's whole reason to exist is that Regulations.gov is cold, dense, and intimidating, so the visual system runs the opposite direction: unhurried spacing, plain language set at readable sizes, and a single warm accent that points the way without raising its voice.

This is a **product** surface, not a marketing showpiece. The design serves one job: get a small-business owner from "a rule might affect me" to a filed, substantive comment. Familiarity is a feature. Buttons look like buttons, filters look like filters, deadlines read like deadlines. Nothing is invented for flavor. The craft shows up in restraint, accurate information, and legibility, because those are what signal that this tool can be trusted with something consequential (a legally binding public comment).

It explicitly rejects three things. It is **not bureaucratic**: no dense gray forms, no cold institutional chrome, no Regulations.gov DNA. It is **not generic SaaS**: no gradient hero, no identical icon-card grid, no buzzword marketing. And it is **not cheap**: nothing that reads as a scam funnel or a throwaway side project.

**Key Characteristics:**
- Warm off-white paper field with near-black ink; a single terracotta accent that earns every appearance.
- Serif body for reading, geometric sans for structure (headings, labels, buttons).
- Flat by default; depth comes from tonal layering, not shadows.
- Generous, varied spacing; content capped at a comfortable reading column (`max-w-2xl`).
- Plain-language copy treated as a first-class design material.

## 2. Colors

A warm, low-saturation paper-and-ink base with one terracotta accent and two muted civic support hues reserved for status.

### Primary
- **Civic Terracotta** (#d97757): The single brand accent. It carries primary actions (the "Continue", "Start interview", "Submit" buttons), the active filter chip, progress fill, the loading spinner, and the most urgent deadline state. It is the only color allowed to compete with the ink for attention, which is exactly why it must stay rare.
- **Terracotta Deep** (#c4634a): The pressed/hover partner for Civic Terracotta. Used only as the hover and active state of accent buttons and accent links.

### Secondary
- **Civic Blue** (#6a9bcc): A muted, non-partisan blue. Used for the mid-urgency deadline state (2–7 days) and the "who this affects" population tags. Calm, informational, never decorative.

### Tertiary
- **Field Olive** (#788c5d): A grounded sage-olive. Used for the low-urgency deadline state (8+ days). Reads as "you have time" without going traffic-light green.

### Neutral
- **Ink** (#141413): Near-black warm charcoal. All primary body text, headings, and the Civly wordmark. The workhorse.
- **Ink Soft** (#6e6960): Warm taupe-gray for genuine secondary text that must still be read, hero subheads, supporting paragraphs, helper copy. Measures ~5.2:1 on `Paper`, so it clears AA while sitting clearly below `Ink` in the hierarchy. This is the correct replacement wherever `Muted` was being misused for readable copy.
- **Paper** (#faf9f5): The warm off-white body background, and the surface of outlined cards and inputs. The reading-room field.
- **Subtle** (#e8e6dc): The soft layering neutral. Borders, dividers, filled card backgrounds (often at 50% alpha over paper), skeleton fills, the progress-bar track, and the disabled-button fill.
- **Muted** (#b0aea5): Low-emphasis text only. Metadata, captions, placeholder text, footers, helper lines. **Contrast-limited (see the rule below).**

### Named Rules
**The Rare Terracotta Rule.** Civic Terracotta marks action and urgency, nothing else. It appears on a small fraction of any screen: the one button you should press next, the active filter, the deadline that is about to close. Never use it as a background wash, a decorative bar, a divider, or an icon tint. Its scarcity is what makes it read as "this is the next step."

**The Muted-Floor Rule.** `Muted` (#b0aea5) on `Paper` (#faf9f5) measures roughly 2:1, far below the 4.5:1 needed for body text. `Muted` is permitted ONLY for genuinely non-essential text (timestamps, character counts, footer credits) and never for sentences the user must read to act. For real secondary copy, use `Ink Soft` (#6e6960, ~5.2:1); for primary copy, `Ink`. Do not reach for `Muted` to make text feel "lighter."

**The Status-Hue Rule.** Blue and Olive exist only to encode deadline urgency and audience, always as a tinted chip (color at ~15% alpha background with the solid hue as text). They are never brand colors and never appear as buttons, headings, or links.

## 3. Typography

**Display / Structure Font:** Poppins (with Arial, sans-serif fallback)
**Body / Reading Font:** Lora (with Georgia, serif fallback)

**Character:** A deliberate contrast pairing, geometric sans against a humanist serif, on the serif-display-plus-sans-body axis flipped: here the **serif carries the reading** and the **sans carries the scaffolding**. Poppins gives headings, labels, and buttons a clean, modern, civic confidence; Lora gives running prose the warmth and authority of a printed page. The split is the point: structure feels built, reading feels human.

### Hierarchy
- **Display** (Poppins 700, 3rem / `text-5xl`, line-height ~1.1): The landing hero headline only. `leading-tight`, drops to `text-4xl` on small screens.
- **Headline** (Poppins 700, 1.5rem / `text-2xl`): Page-level titles, e.g. a rule's title on its detail page.
- **Title** (Poppins 600, 1.125rem / `text-lg`; or 1rem / `text-base` semibold for sub-sections): Section headings ("What your comment should argue", "Why your comment matters").
- **Body** (Lora 400, 1rem / `text-base`; compact UI uses 0.875rem / `text-sm`): All reading copy, rule summaries, explanatory text. Keep prose to a 65–75ch column; the `max-w-2xl` page width already enforces this.
- **Label** (Poppins 500, 0.75rem / `text-xs`): Metadata, deadline badges, "Point 1", character counts, agency IDs, footer credits.

### Named Rules
**The Sans-For-Structure Rule.** Anything that is chrome rather than content, buttons, filter chips, badges, section headings, the wordmark, progress labels, is set in Poppins (`font-heading`). Anything the user reads as a sentence is set in Lora. Never set body prose in Poppins, and never set a button label in Lora.

**The No-Shout Rule.** Display tops out at 3rem (~48px). Civly informs, it does not shout; there is no oversized clamp hero. Letter-spacing stays at `normal`, never tightened past it.

## 4. Elevation

Civly is **flat by default with tonal layering**. Depth is built from the neutral ramp, not from shadows: a panel separates from the page by sitting on `Subtle` (often `bg-subtle/50`) or by carrying a 1px `Subtle` border, not by floating. This keeps the reading-room calm and avoids the "2014 app" look of heavy drop shadows.

Shadows appear only as a **response to state**, never at rest. The single resting exception is the marketing screenshot on the landing page (`shadow-2xl`), which is presentational, not part of the app UI.

### Shadow Vocabulary
- **Hover lift** (`box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` / Tailwind `shadow-md`): Applied to a Rule Card on hover, paired with a background shift from `subtle/50` to `paper`. Communicates "this row is interactive."

### Named Rules
**The Flat-At-Rest Rule.** Surfaces are flat when idle. If you see a drop shadow on a card, input, or panel in its default state, it is wrong; reach for a `Subtle` border or a `Subtle` fill instead. Shadow is a verb (hover, focus), not a decoration.

## 5. Components

Components are **calm and legible**: quiet, unhurried, standard in shape, nothing competing for attention. Consistency screen to screen is a virtue here, not a missed chance to delight.

### Buttons
- **Shape:** Gently rounded (8px, `rounded-lg`). Set in Poppins (`font-heading`), weight 500–600.
- **Primary:** `Civic Terracotta` fill, `Paper` text, `12px 24px` padding (`px-6 py-3`); the landing hero CTA is larger at `px-8 py-4`. Full-width on mobile, auto on `sm+` where appropriate.
- **Hover / Focus:** `transition-colors` to `Terracotta Deep`. (Focus-visible rings are an open gap; see Don'ts.)
- **Disabled:** `Subtle` fill, `Muted` text, `cursor-not-allowed`. Used for in-flight states ("Thinking…", "Starting interview…") and not-yet-available actions ("Draft my comment").

### Chips
- **Filter chips (AgencyFilter):** Pill-shaped (`rounded-full`), `4px 12px` padding, Poppins 500 `text-sm`. **Selected** = `Civic Terracotta` fill, `Paper` text. **Unselected** = `Paper` fill, 1px `Subtle` border, `Muted` text, hover to `subtle/50`. Toggling the active chip clears the filter.
- **Deadline badge:** Pill-shaped, `text-xs` Poppins 500, tinted by urgency: ≤1 day = terracotta tint, 2–7 days = blue tint, 8+ days = olive tint (hue at ~15% alpha background, solid hue as text). Always `whitespace-nowrap shrink-0`.
- **Population tag:** Blue-tinted pill (`secondary/15` bg, `Civic Blue` text) listing who a rule affects.

### Cards / Containers
- **Corner Style:** 8px (`rounded-lg`).
- **Two variants:** **Filled** (`bg-subtle/50`) for soft content blocks (rule rows, analysis summary, strengthening suggestions); **Outlined** (1px `Subtle` border on `Paper`) for structured info blocks (deadline block, "why your comment matters", argument points).
- **Shadow Strategy:** None at rest. Rule Cards add `shadow-md` + background shift to `Paper` on hover (see Elevation).
- **Internal Padding:** `16px` (`p-4`) for compact rows, `24px` (`p-6`) for content panels.
- **Never nest a card inside a card.**

### Inputs / Fields
- **Style:** 1px `Subtle` border on `Paper`, 8px radius, `12px 16px` padding, `text-sm` `Ink`, placeholder in `Muted`.
- **Focus:** Border shifts to `Civic Terracotta` plus a 1px terracotta ring (`focus:border-accent focus:ring-1 focus:ring-accent`), no glow. Auto-focused on each new interview step.
- **Disabled:** Dims during submission; paired with a live character count below.

### Navigation
- **Style:** Minimal. The "Civly" wordmark in Poppins (semibold/bold `Ink`) sits top-left; detail pages add a `← Back` link in `Civic Terracotta`. No persistent top bar or side nav; the product is a short linear flow (browse → rule → interview → result), so navigation stays out of the way.

### Signature Components
- **Progress bar (InterviewStep):** A slim `h-1.5` `rounded-full` track in `Subtle` with a `Civic Terracotta` fill, `transition-all duration-300`, labeled "N of ~4". Sets expectations for an open-ended interview without over-promising.
- **Loading spinner:** `h-6 w-6`, `border-2` `Civic Terracotta` with a transparent top, `animate-spin`. Used for discrete waits (building the argument, analyzing a rule) with a plain-language caption.
- **Skeletons:** `animate-pulse` `Subtle` blocks that mirror the real layout (filter pills, rule rows, the rule title). Loading uses skeletons for content shape and spinners only for discrete background work, never a bare spinner where content will land.
- **Deadline block:** Pairs a Deadline Badge with the plain-language promise that comments "are legally required to be considered," plus an outbound Regulations.gov link. This is Civly's trust anchor; keep its language exact and never overstate it.

## 6. Do's and Don'ts

### Do:
- **Do** keep `Civic Terracotta` (#d97757) rare: primary action, active filter, urgent deadline, progress. One clear "next step" per screen.
- **Do** set reading copy in Lora and all chrome (buttons, labels, headings, chips, wordmark) in Poppins.
- **Do** convey depth with the neutral ramp, a `Subtle` border or a `bg-subtle/50` fill, and keep surfaces flat at rest.
- **Do** use skeletons that mirror the final layout for content loads, and reserve spinners for discrete background work with a plain-language caption.
- **Do** cap prose at the `max-w-2xl` reading column and let spacing vary for rhythm (`p-4` rows, `p-6` panels, generous section gaps).
- **Do** write deadline and "legally binding" copy precisely; accuracy is the trust signal.

### Don't:
- **Don't** look bureaucratic. No dense gray forms, no cold institutional chrome, nothing that inherits Regulations.gov's tone or layout. Civly exists to replace that experience.
- **Don't** look like generic SaaS. No gradient hero, no identical icon + heading + text card grids, no buzzword marketing copy ("streamline", "empower", "seamless").
- **Don't** look cheap or untrustworthy. The product handles a legally binding public record; sloppy craft or scammy funnel patterns break the whole premise.
- **Don't** use `border-left`/`border-right` greater than 1px as a colored accent stripe on cards or callouts. (The landing's three value props currently violate this with `border-l-[3px]`; rewrite with full borders or no border.)
- **Don't** set essential body text in `Muted` (#b0aea5) on `Paper`; it fails contrast at ~1.9:1. Muted is for non-essential metadata only.
- **Don't** put drop shadows on resting cards, inputs, or panels. Shadow is a hover/focus response, not decoration.
- **Don't** use gradient text, decorative glassmorphism, or per-section uppercase tracked eyebrows.
- **Don't** apply `Civic Blue` or `Field Olive` as brand colors; they are status tints only.
