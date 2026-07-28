/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingIncludes: {
    "/api/**": ["./data/etf_screener.sqlite"],
    "/**": ["./data/etf_screener.sqlite"],
  },
};

module.exports = nextConfig;
