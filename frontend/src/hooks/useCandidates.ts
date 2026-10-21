"use client";

import { useState, useEffect, useCallback } from "react";
import { candidateService } from "@/services";
import type { Candidate } from "@/types";

export function useCandidates(params?: { limit?: number; skip?: number }) {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCandidates = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await candidateService.getCandidates(params);
      setCandidates(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch candidates.");
    } finally {
      setIsLoading(false);
    }
  }, [params?.limit, params?.skip]);

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  return { candidates, total, isLoading, error, refetch: fetchCandidates };
}