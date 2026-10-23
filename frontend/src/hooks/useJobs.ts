// src/hooks/useJobs.ts

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { jobService } from "@/services";
import type { Job, JobQueryParams } from "@/types";

export function useJobs(params?: JobQueryParams) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Extract primitive values to prevent object reference re-trigger loops in useEffect
  const page = params?.page ?? 1;
  const size = params?.size ?? 10;
  const search = params?.search ?? "";
  const status = params?.status;
  const department = params?.department;
  const workModel = params?.work_model;

  const fetchJobs = useCallback(async (signal?: AbortSignal) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await jobService.getJobs(
        {
          page,
          size,
          search: search || undefined,
          status,
          department,
          work_model: workModel,
        },
        signal
      );
      
      setJobs(response.items);
      setTotal(response.total);
      setTotalPages(response.pages);
    } catch (err: any) {
      if (err?.name === "AbortError" || err?.code === "ERR_CANCELED") {
        return; // Request was canceled; skip state update
      }
      setError(err?.message || "Failed to fetch job requisitions.");
    } finally {
      setIsLoading(false);
    }
  }, [page, size, search, status, department, workModel]);

  useEffect(() => {
    const controller = new AbortController();
    fetchJobs(controller.signal);

    return () => {
      controller.abort();
    };
  }, [fetchJobs]);

  return {
    jobs,
    total,
    totalPages,
    currentPage: page,
    isLoading,
    error,
    refetch: () => fetchJobs(),
  };
}