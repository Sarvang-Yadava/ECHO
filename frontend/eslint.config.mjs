import { defineConfig, globalIgnores } from "eslint/config";

// `eslint-config-next@15` still exports legacy config. Keep this flat config
// compatible with ESLint 9; Next performs its own compile-time checks in build.
export default defineConfig([
  globalIgnores([".next/**", "node_modules/**"]),
]);
