/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@sambal/contracts"],
  async rewrites() {
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8093";
    return [
      {
        source: "/api/backend/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

const deploymentEnvironment = process.env.NEXT_PUBLIC_APP_ENV;
const quickExitUrl = process.env.NEXT_PUBLIC_QUICK_EXIT_URL;
if (
  (deploymentEnvironment === "production" ||
    deploymentEnvironment === "staging") &&
  (!quickExitUrl ||
    !/^https:\/\//i.test(quickExitUrl) ||
    /sambal|localhost|127\.0\.0\.1|\[::1\]/i.test(quickExitUrl))
) {
  throw new Error(
    "NEXT_PUBLIC_QUICK_EXIT_URL must be an approved neutral HTTPS destination for production and staging.",
  );
}

export default nextConfig;
