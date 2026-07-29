"use client";

import { useCallback, useEffect, useState } from "react";
import {
  DEFAULT_INFLATION_PCT,
  DEFAULT_REAL_GROWTH_PCT,
  EtfPremises,
  defaultPremises,
} from "@/lib/expectedReturn";

const STORAGE_KEY = "etf-screener:premises-v1";

type PremisesMap = Record<string, EtfPremises>;

function readStore(): PremisesMap {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as PremisesMap;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function writeStore(map: PremisesMap): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
}

function normalizePremises(value: Partial<EtfPremises> | undefined): EtfPremises {
  const inflation =
    typeof value?.inflationPct === "number" && Number.isFinite(value.inflationPct)
      ? value.inflationPct
      : DEFAULT_INFLATION_PCT;
  const realGrowth =
    typeof value?.realGrowthPct === "number" && Number.isFinite(value.realGrowthPct)
      ? value.realGrowthPct
      : DEFAULT_REAL_GROWTH_PCT;
  return { inflationPct: inflation, realGrowthPct: realGrowth };
}

/** Lê e grava premissas por ticker no localStorage do navegador. */
export function useEtfPremises() {
  const [store, setStore] = useState<PremisesMap>({});
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setStore(readStore());
    setReady(true);
  }, []);

  const getPremises = useCallback(
    (ticker: string): EtfPremises => {
      const key = ticker.toUpperCase();
      return normalizePremises(store[key] ?? defaultPremises());
    },
    [store],
  );

  const setPremises = useCallback((ticker: string, next: Partial<EtfPremises>) => {
    const key = ticker.toUpperCase();
    setStore((prev) => {
      const merged = normalizePremises({ ...normalizePremises(prev[key]), ...next });
      const updated = { ...prev, [key]: merged };
      writeStore(updated);
      return updated;
    });
  }, []);

  return { getPremises, setPremises, ready };
}
