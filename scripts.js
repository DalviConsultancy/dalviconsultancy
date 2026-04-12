document.addEventListener('DOMContentLoaded', () => {


    // Custom Smooth Scroll (easeInOutQuad)
    // Applies to all anchor links starting with #
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#' || targetId === '') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                const duration = 1000; // 1 second duration for "slow start/finish" feel
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
                const startPosition = window.pageYOffset;
                const distance = targetPosition - startPosition;
                let startTime = null;

                function animation(currentTime) {
                    if (startTime === null) startTime = currentTime;
                    const timeElapsed = currentTime - startTime;
                    const run = easeInOutQuad(timeElapsed, startPosition, distance, duration);
                    window.scrollTo(0, run);
                    if (timeElapsed < duration) requestAnimationFrame(animation);
                }

                // Easing function: fast in middle, slow start/end
                function easeInOutQuad(t, b, c, d) {
                    t /= d / 2;
                    if (t < 1) return c / 2 * t * t + b;
                    t--;
                    return -c / 2 * (t * (t - 2) - 1) + b;
                }

                requestAnimationFrame(animation);
            }
        });
    });

    // Mobile Menu Logic
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const mobileMenuCloseBtn = document.getElementById('mobile-menu-close');
    const mobileMenuLinks = document.querySelectorAll('#mobile-menu-overlay a');

    function toggleMenu() {
        const isClosed = mobileMenuOverlay.classList.contains('translate-x-full');
        if (isClosed) {
            mobileMenuOverlay.classList.remove('translate-x-full');
            document.body.classList.add('overflow-hidden');
        } else {
            mobileMenuOverlay.classList.add('translate-x-full');
            document.body.classList.remove('overflow-hidden');
        }
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMenu);
    }

    if (mobileMenuCloseBtn) {
        mobileMenuCloseBtn.addEventListener('click', toggleMenu);
    }

    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', toggleMenu);
    });
});
