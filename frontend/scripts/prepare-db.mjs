import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.join(__dirname, "..");
const repoRoot = path.join(frontendRoot, "..");
const target = path.join(frontendRoot, "data", "etf_screener.sqlite");
const source = path.join(repoRoot, "data", "database", "etf_screener.sqlite");
const exportDir = path.join(repoRoot, "exports", "schy_piloto_2026-07-27");

fs.mkdirSync(path.dirname(target), { recursive: true });

if (fs.existsSync(source)) {
  fs.copyFileSync(source, target);
  console.log("Banco copiado de data/database/ para frontend/data/");
} else if (fs.existsSync(target)) {
  console.log("Usando banco existente em frontend/data/");
} else if (fs.existsSync(exportDir)) {
  console.log("Gerando banco a partir dos CSVs do piloto SCHY...");
  execSync("python3 scripts/seed_schy_pilot.py", { cwd: repoRoot, stdio: "inherit" });
  execSync("python3 scripts/calculate_etf_metrics.py --etf SCHY", { cwd: repoRoot, stdio: "inherit" });
  fs.copyFileSync(source, target);
  console.log("Banco gerado e copiado para frontend/data/");
} else {
  throw new Error(
    "Banco SQLite não encontrado. Rode localmente: python3 scripts/seed_schy_pilot.py",
  );
}
