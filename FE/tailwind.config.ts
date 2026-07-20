import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6eaf2',
          100: '#c2ccd9',
          200: '#9aacbe',
          300: '#718ca3',
          400: '#52748d',
          500: '#335c77',
          600: '#2e536b',
          700: '#27485b',
          800: '#203e4c',
          900: '#152e3a',
          950: '#0a1a22',
        },
        navy: {
          50: '#e7e9ef',
          100: '#c4c9d7',
          200: '#9da5bf',
          300: '#7681a7',
          400: '#586794',
          500: '#3a4d81',
          600: '#334579',
          700: '#2b3b6e',
          800: '#233264',
          900: '#16234f',
          950: '#0d1632',
        },
        gold: {
          50: '#fffce6',
          100: '#fff8cc',
          200: '#fff199',
          300: '#ffe866',
          400: '#ffde33',
          500: '#FFCF0E',
          600: '#e6ba0c',
          700: '#cca50a',
          800: '#b39009',
          900: '#997b07',
        },
      },
      fontFamily: {
        montserrat: ['Montserrat', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
