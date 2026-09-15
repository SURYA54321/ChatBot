import { useEffect, useRef, useState } from "react";

// Decouples how fast text *arrives* from how fast it's *displayed*.
// Feed it the full target string (grows as tokens stream in); it reveals
// characters at a steady pace, speeding up automatically to catch up if a
// big chunk lands at once, so a burst doesn't sit there typing forever.
function useTypewriter(targetText, { charsPerSecond = 55, active = true, catchUpSeconds = 1.2 } = {}) {
    const [displayed, setDisplayed] = useState(active ? "" : targetText);
    const displayedRef = useRef(displayed);
    const targetRef = useRef(targetText);
    const runningRef = useRef(false);
    const lastTimeRef = useRef(null);

    targetRef.current = targetText;

    useEffect(() => {
        if (!active) {
            displayedRef.current = targetText;
            setDisplayed(targetText);
            return;
        }

        // Content was replaced rather than extended (e.g. a retry) — restart the reveal.
        if (!targetText.startsWith(displayedRef.current)) {
            displayedRef.current = "";
            setDisplayed("");
        }

        if (runningRef.current) return;
        runningRef.current = true;

        function tick(now) {
            if (lastTimeRef.current == null) lastTimeRef.current = now;
            const dt = (now - lastTimeRef.current) / 1000;
            lastTimeRef.current = now;

            const target = targetRef.current;
            const current = displayedRef.current;

            if (current.length < target.length) {
                const backlog = target.length - current.length;
                const rate = Math.max(charsPerSecond, backlog / catchUpSeconds);
                const charsToAdd = Math.max(1, Math.round(rate * dt));

                const next = target.slice(0, Math.min(target.length, current.length + charsToAdd));
                displayedRef.current = next;
                setDisplayed(next);
                requestAnimationFrame(tick);
            } else {
                runningRef.current = false;
                lastTimeRef.current = null;
            }
        }

        requestAnimationFrame(tick);
    }, [targetText, active, charsPerSecond, catchUpSeconds]);

    return displayed;
}

export default useTypewriter;