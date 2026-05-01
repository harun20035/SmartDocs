"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import styles from "./Upload.module.css";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  const router = useRouter();

  function handleFileChange(e) {
    setFile(e.target.files[0]);
  }

  async function handleUpload() {
    if (!file) {
      setError("Please select a file");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("${API_URL}/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Upload failed");
      }

      const data = await res.json();
      const documentId = data.id;

      const processRes = await fetch(
        `${API_URL}/documents/${documentId}/process`,
        { method: "POST" }
      );

      if (!processRes.ok) {
        const errData = await processRes.json().catch(() => ({}));
        throw new Error(errData.detail || "Processing failed");
      }

      router.push(`/documents/${documentId}`);
    } catch (err) {
      console.error(err);
      setError(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Upload Document</h1>
        <p className={styles.subtitle}>
          Upload a CSV, TXT, or PDF file. The system will extract fields and validate
          the document automatically.
        </p>

        <input
          type="file"
          onChange={handleFileChange}
          className={styles.input}
        />
        {file && <p className={styles.fileName}>Selected: {file.name}</p>}

        <button
          onClick={handleUpload}
          disabled={loading}
          className={styles.button}
        >
          {loading ? "Uploading..." : "Upload"}
        </button>

        {error && <p className={styles.error}>{error}</p>}
        <Link href="/" className={styles.backLink}>
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}