/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "rgba(255,255,255,0.10)",
        "border-subtle": "rgba(255,255,255,0.06)",
        input: "rgba(255,255,255,0.10)",
        ring: "#3B82F6",
        background: "#09090B",
        foreground: "#FAFAFA",
        primary: {
          DEFAULT: "#FAFAFA",
          foreground: "#09090B",
        },
        secondary: {
          DEFAULT: "#18181B",
          foreground: "#A1A1AA",
        },
        destructive: {
          DEFAULT: "#EF4444",
          foreground: "#FAFAFA",
        },
        muted: {
          DEFAULT: "#18181B",
          foreground: "#71717A",
        },
        accent: {
          DEFAULT: "#3B82F6",
          hover: "#2563EB",
          subtle: "rgba(59,130,246,0.12)",
          foreground: "#FAFAFA",
        },
        success: {
          DEFAULT: "#22C55E",
          foreground: "#FAFAFA",
        },
        warning: {
          DEFAULT: "#EAB308",
          foreground: "#FAFAFA",
        },
        popover: {
          DEFAULT: "#18181B",
          foreground: "#FAFAFA",
        },
        card: {
          DEFAULT: "#0F0F12",
          foreground: "#FAFAFA",
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "calc(0.5rem - 2px)",
        sm: "calc(0.5rem - 4px)",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "shimmer": {
          "100%": {
            transform: "translateX(100%)",
          },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
