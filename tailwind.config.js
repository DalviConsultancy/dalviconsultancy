/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./*.{html,js}", "./projects/*.html"],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                primary:           "#0EA5E9",
                "primary-dark":    "#0284C7",
                "background-dark": "#030712",
                "surface":         "rgba(255,255,255,0.03)",
            },
            fontFamily: {
                display: ["Plus Jakarta Sans", "sans-serif"],
                sans:    ["Inter", "sans-serif"],
            },
            borderRadius: {
                DEFAULT: "0.5rem",
                sm:   "0.25rem",
                md:   "0.375rem",
                lg:   "0.5rem",
                xl:   "0.75rem",
                "2xl":"1rem",
                "3xl":"1.5rem",
                full: "9999px",
            },
            boxShadow: {
                "glow-sm":  "0 0 15px rgba(14,165,233,0.15)",
                "glow":     "0 0 30px rgba(14,165,233,0.20)",
                "glow-lg":  "0 0 60px rgba(14,165,233,0.25)",
                "card":     "0 4px 24px rgba(0,0,0,0.4)",
                "card-hover":"0 20px 40px rgba(0,0,0,0.5)",
            },
            backgroundImage: {
                "gradient-primary": "linear-gradient(135deg,#0EA5E9,#6366F1)",
                "gradient-hero":    "radial-gradient(ellipse 80% 50% at 50% -20%,rgba(14,165,233,0.15),transparent)",
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
        require('@tailwindcss/forms'),
    ],
}
