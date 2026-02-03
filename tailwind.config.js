/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        brand: '#8a1538',
        brand_dark: '#70102d',
        dark: '#0f172a', // Этот цвет теперь корректно подхватится классом text-dark
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.05)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'), // <--- ОБЯЗАТЕЛЬНО ДОБАВИТЬ ЭТУ СТРОКУ
  ],
}