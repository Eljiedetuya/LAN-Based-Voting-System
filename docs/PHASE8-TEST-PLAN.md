# Phase 8 frontend test checklist

1. Launch Vite and open `/`; each demo role enters its own navigation layout.
2. Student: dashboard → elections → candidates → profile → back → ballot. Choose one candidate in each of 3 positions. Navigate to Review; use Edit and verify selections are preserved.
3. Review screen: verify the final vote button is disabled, and no POST request is made by clicking it.
4. Directly visit `/student/confirmation`: verify it explicitly says no vote was submitted.
5. Student status: verify it says unverified/unknown, not accepted.
6. Admin: open each sidebar destination, use candidate and voter search, preview create/edit forms, and verify Save buttons are disabled.
7. Monitor: open all four pages; verify counts clearly say illustrative/mock and no user-level vote selections are shown.
8. Django API health: run and stop backend; verify the role chooser distinguishes reachable/unreachable. A one-time check runs at load, not live monitoring.
9. Direct `/login`: verify sign-in is disabled and credentials are not sent. No backend auth exists.
10. Reload `/student/ballot`: verify selections are not persisted in browser storage.
11. Check viewport widths 360px, 768px, 1280px, 200% zoom; no ballot clipping and all primary actions visible.
12. Keyboard: navigate through radio buttons, forms, links, and focus-visible states. Verify semantic headings, labels and status messages.
13. `npm run build`: must complete with no errors.

Tests 1–12 require a browser and installed frontend dependencies. They are NOT claimed to have passed merely because source files exist.
