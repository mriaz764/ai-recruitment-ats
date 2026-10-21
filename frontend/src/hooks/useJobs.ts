"use client";

import { useState, useEffect, useCallback } from "react";
import { jobService } from "@/services";
import type { Job } from "@/types";

export function useJobs(params?: { limit?: number; skip?: number }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await jobService.getJobs(params);
      setJobs(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch jobs.");
    } finally {
      setIsLoading(false);
    }
  }, [params?.limit, params?.skip]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return { jobs, total, isLoading, error, refetch: fetchJobs };
}