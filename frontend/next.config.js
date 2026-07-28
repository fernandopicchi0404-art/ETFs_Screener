/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ["better-sqlite3"],
  outputFileTracingIncludes: {
    "/api/**": ["./data/etf_screener.sqlite"],
    "/**": ["./data/etf_screener.sqlite"],
    "/etf/[ticker]": ["./data/etf_screener.sqlite"],
    "/ativos": ["./data/etf_screener.sqlite"],
  },
};

module.exports = nextConfig;
