/**
 * Confetti Celebration Animation
 * Realistic fireworks-style confetti for celebrating successful submissions
 */

/**
 * Triggers a celebratory confetti animation
 * Launches fireworks from the bottom center of the screen
 */
function triggerConfetti() {
    const duration = 4000; // 4 seconds
    const animationEnd = Date.now() + duration;

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    // First big firework from bottom center - WIDER SPREAD
    confetti({
        particleCount: 120,
        angle: 90,
        spread: 110,
        origin: { x: 0.5, y: 1.0 }, // Bottom center
        colors: ['#28a745', '#20c997', '#ffc107', '#17a2b8'],
        startVelocity: 75,
        gravity: 1,
        drift: 0,
        ticks: 200,
        zIndex: 9999,
        scalar: 2.0  // Much larger particles
    });

    // Second firework slightly delayed - LEFT SIDE
    setTimeout(() => {
        confetti({
            particleCount: 100,
            angle: 90,
            spread: 100,
            origin: { x: 0.35, y: 1.0 },
            colors: ['#007bff', '#20c997', '#ffc107'],
            startVelocity: 70,
            gravity: 1,
            ticks: 200,
            zIndex: 9999,
            scalar: 1.8  // Larger particles
        });
    }, 300);

    // Third firework - RIGHT SIDE
    setTimeout(() => {
        confetti({
            particleCount: 100,
            angle: 90,
            spread: 100,
            origin: { x: 0.65, y: 1.0 },
            colors: ['#28a745', '#dc3545', '#ffc107'],
            startVelocity: 70,
            gravity: 1,
            ticks: 200,
            zIndex: 9999,
            scalar: 1.8  // Larger particles
        });
    }, 600);

    // Continuous smaller bursts - WIDER COVERAGE
    const interval = setInterval(function() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) {
            return clearInterval(interval);
        }

        const particleCount = 40 * (timeLeft / duration);

        // Random position across bottom - WIDER RANGE
        confetti({
            particleCount,
            angle: randomInRange(75, 105),
            spread: randomInRange(80, 110),
            origin: { 
                x: randomInRange(0.3, 0.7),  // Wider horizontal range
                y: 1.0 
            },
            colors: ['#28a745', '#20c997', '#17a2b8', '#ffc107', '#007bff'],
            startVelocity: randomInRange(55, 70),
            gravity: 1,
            drift: randomInRange(-1, 1),  // More drift for wider spread
            ticks: 200,
            zIndex: 9999,
            scalar: randomInRange(1.5, 2.2)  // Larger particles
        });
    }, 400);

    // Grand finale burst at 2.5 seconds - MASSIVE SPREAD
    setTimeout(() => {
        confetti({
            particleCount: 200,
            angle: 90,
            spread: 140,
            origin: { x: 0.5, y: 1.0 },
            colors: ['#28a745', '#20c997', '#17a2b8', '#ffc107', '#007bff', '#dc3545'],
            startVelocity: 90,
            gravity: 0.8,
            drift: 0,
            ticks: 250,
            zIndex: 9999,
            scalar: 2.5,  // Largest particles
            shapes: ['circle', 'square']
        });
    }, 2500);
}

/**
 * Optional: Trigger a smaller, quicker confetti burst
 * Useful for smaller achievements or milestones
 */
function triggerMiniConfetti() {
    confetti({
        particleCount: 50,
        angle: 90,
        spread: 70,
        origin: { x: 0.5, y: 1.0 },
        colors: ['#28a745', '#20c997', '#ffc107'],
        startVelocity: 60,
        gravity: 1,
        ticks: 150,
        zIndex: 9999,
        scalar: 1.5
    });
}

