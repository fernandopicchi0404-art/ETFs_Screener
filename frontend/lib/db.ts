import Database from "better-sqlite3";
import fs from "fs";
import path from "path";

let db: Database.Database | null = null;

function resolveDbPath(): string {
  const candidates = [
    path.join(process.cwd(), "data", "etf_screener.sqlite"),
    path.join(process.cwd(), "frontend", "data", "etf_screener.sqlite"),
    path.join(__dirname, "..", "data", "etf_screener.sqlite"),
    path.join(__dirname, "..", "..", "data", "etf_screener.sqlite"),
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  throw new Error(
    "Banco SQLite não encontrado. Rode: python3 scripts/seed_schy_pilot.py && npm run prepare-db",
  );
}

export function getDb(): Database.Database {
  if (!db) {
    db = new Database(resolveDbPath(), { readonly: true, fileMustExist: true });
  }
  return db;
}

export function pct(value: number | null | undefined): number | null {
  if (value === null || value === undefined) return null;
  return Math.round(value * 10000) / 100;
}
