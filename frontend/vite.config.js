import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],

  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          minSize: 20_000,

          groups: [
            {
              name: "react-vendor",
              test:
                /node_modules[\\/](react|react-dom|scheduler)[\\/]/,
              priority: 30,
              maxSize: 250_000,
            },
            {
              name: "mui-vendor",
              test:
                /node_modules[\\/](@mui|@emotion)[\\/]/,
              priority: 20,
              maxSize: 300_000,
            },
            {
              name: "motion-vendor",
              test:
                /node_modules[\\/]framer-motion[\\/]/,
              priority: 15,
              maxSize: 250_000,
            },
            {
              name: "vendor",
              test: /node_modules/,
              priority: 10,
              maxSize: 250_000,
            },
          ],
        },
      },
    },
  },
});
