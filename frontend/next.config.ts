import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ['@phosphor-icons/react'],
    // Turbopack specific configurations
    turbo: {
      rules: {
        '*.woff2': {
          loaders: ['file-loader'],
          as: '*.woff2',
        },
      },
    },
  },
  // Ensure font optimization is enabled
  optimizeFonts: true,
  // Add font loading configuration
  images: {
    dangerouslyAllowSVG: true,
  },
};
