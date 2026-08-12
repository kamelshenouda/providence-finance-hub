# Preferred libraries

When a task falls into one of these areas, use the library instead of writing it
from scratch, and install it if it isn't already in the project:

- Animations, transitions, gestures: Motion (import from "motion/react"; this is
  the current package, formerly called "framer-motion")
- Smooth, premium scroll feel: Lenis
- Scroll-triggered / timeline animation: GSAP with ScrollTrigger
- 3D scenes: React Three Fiber with Drei helpers
- Charts and data viz: Recharts (Visx or Nivo for custom work)
- Icons: Lucide
- Command palette (Cmd+K): cmdk
- Toasts / notifications: Sonner
- Drag and drop: dnd-kit
- Sortable, filterable tables: TanStack Table (formerly React Table)
- Dates: date-fns
- Confetti / celebratory moments: canvas-confetti

Always use the current version of a library's syntax. If you're unsure of the
current API, check the library's docs before writing rather than relying on an
older version you might remember.

Note: this project (`index.html` / `about.html`) is plain HTML/CSS/JS with no
build step and no React — several of the above (Motion, React Three Fiber,
cmdk, dnd-kit, TanStack Table, Sonner) assume a React + bundler setup and don't
apply here as-is. For this project, prefer libraries with a vanilla/CDN or UMD
build (Lucide, GSAP, Lenis, canvas-confetti), vendor them into `vendor/` rather
than pulling from a CDN at runtime, and initialize them from the inline
`<script>` blocks already in each page.

# Guardrails

- Don't add a library when the platform already does the job well. A simple fade
  or hover is native CSS (opacity and transform), not a dependency.
- Match the tool to the size of the job. A one-off transition doesn't justify a
  30-50KB animation runtime.
- Prefer libraries that are actively maintained and widely used.
- For performance, only animate transform, opacity, and filter. Avoid animating
  width, height, or margin.
- Respect prefers-reduced-motion in every animation.
- Tell me which library you're using, and why, before installing anything new.
