import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  // Webpack: resolve o prefixo ~ do SCSS do Carbon para node_modules (sass-loader)
  webpack(config) {
    config.resolve.alias = {
      ...config.resolve.alias,
      "~": path.resolve("node_modules"),
    };
    return config;
  },
};

export default nextConfig;
