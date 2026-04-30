"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import styles from "./Dashboard.module.css";

export default function DashboardPage() {
  const [documents, setDocuments] = useState([]);
  const [totalsByCurrency, setTotalsByCurrency] = useState({});
  const [totalDocuments, setTotalDocuments] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const LIMIT = 10;

  useEffect(() => {
    fetchDocuments(true);
  }, []);

  async function fetchDocuments(reset = false) {
    try {
      if (reset) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      const currentOffset = reset ? 0 : offset;
      const res = await fetch(
        `http://localhost:8000/dashboard?offset=${currentOffset}&limit=${LIMIT}`
      );
      const data = await res.json();

      if (reset) {
        setDocuments(data.items ?? []);
        setTotalsByCurrency(data.totals_by_currency ?? {});
        setTotalDocuments(data.total ?? 0);
      } else {
        setDocuments((prev) => [...prev, ...(data.items ?? [])]);
      }
      setOffset(currentOffset + (data.items?.length ?? 0));
      setHasMore(Boolean(data.has_more));
    } catch (error) {
      console.error("Error fetching documents:", error);
    } finally {
      if (reset) {
        setLoading(false);
      } else {
        setLoadingMore(false);
      }
    }
  }

  if (loading) {
    return (
      <div className={styles.loaderWrapper}>
        <div className={styles.spinner}></div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Documents Dashboard</h1>
        <Link href="/upload" className={styles.primaryAction}>
          Upload Document
        </Link>
      </div>

      <div className={styles.metaRow}>
        <p className={styles.totalText}>
          Showing {documents.length} of {totalDocuments} documents
        </p>
      </div>

      {Object.keys(totalsByCurrency).length > 0 && (
        <div className={styles.currencyGrid}>
          {Object.entries(totalsByCurrency).map(([currency, amount]) => (
            <div key={currency} className={styles.currencyCard}>
              <p className={styles.currencyLabel}>{currency}</p>
              <p className={styles.currencyAmount}>{Number(amount).toFixed(2)}</p>
            </div>
          ))}
        </div>
      )}

      <table className={styles.table}>
        <thead>
          <tr>
            <th>ID</th>
            <th>File Name</th>
            <th>Status</th>
            <th>Issues</th>
          </tr>
        </thead>

        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td>{doc.id}</td>
              <td>
                <Link href={`/documents/${doc.id}`} className={styles.fileLink}>
                  {doc.file_name}
                </Link>
              </td>
              <td>
                <span className={`${styles.status} ${styles[doc.status] ?? ""}`}>
                  {doc.status}
                </span>
              </td>
              <td>{doc.error_count ?? doc.issues ?? 0}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {hasMore && (
        <div className={styles.loadMoreWrap}>
          <button
            className={styles.primaryAction}
            onClick={() => fetchDocuments(false)}
            disabled={loadingMore}
          >
            {loadingMore ? "Loading..." : "Load more"}
          </button>
        </div>
      )}
    </div>
  );
}