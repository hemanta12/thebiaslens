/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  important: true, // Makes all Tailwind utilities !important to override MUI
  theme: {
    extend: {},
  },
  plugins: [],
};
