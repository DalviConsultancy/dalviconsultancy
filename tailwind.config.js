/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./*.{html,js}", "./execution/*.py"],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                primary: "#0EA5E9",
                "background-light": "#F8FAFC",
                "background-dark": "#030712",
                accent: { cyan: "#22D3EE", blue: "#2563EB" }
            },
            fontFamily: {
                display: ["Plus Jakarta Sans", "sans-serif"],
                sans: ["Inter", "sans-serif"],
            },
            borderRadius: { DEFAULT: "1rem", '2xl': "1.5rem" },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
        require('@tailwindcss/forms'),
    ],
}
