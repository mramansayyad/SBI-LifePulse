/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sbi: {
          blue: "#1B4F8E",
          orange: "#F7941D",
          dark: "#1A1A2E",
          light: "#F5F7FA",
        },
        success: "#22C55E",
        danger: "#EF4444",
        text: {
          primary: "#1A1A2E",
          secondary: "#6B7280",
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
