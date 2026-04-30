"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import Link from "next/link";
import styles from "./DocumentDetail.module.css";

export default function DocumentDetailPage({ params }) {
  const { id } = use(params);

  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [showValidationModal, setShowValidationModal] = useState(false);
  const [validationModalMessage, setValidationModalMessage] = useState("");

  useEffect(() => {
    fetchDocument();
  }, [id]);

  async function fetchDocument() {
    try {
      setLoading(true);

      const res = await fetch(`http://localhost:8000/documents/${id}`);

      if (!res.ok) {
        throw new Error(`Failed to fetch document (${res.status})`);
      }

      const data = await res.json();
      setDocument(data);
      setForm({
        document_type: data.document_type ?? "",
        supplier_name: data.supplier_name ?? "",
        document_number: data.document_number ?? "",
        issue_date: data.issue_date ?? "",
        due_date: data.due_date ?? "",
        currency: data.currency ?? "",
        subtotal: data.subtotal ?? 0,
        tax: data.tax ?? 0,
        total: data.total ?? 0,
        line_items:
          data.line_items?.map((item) => ({
            description: item.description ?? "",
            quantity: item.quantity ?? 0,
            unit_price: item.unit_price ?? 0,
            total: item.total ?? 0,
          })) ?? [],
      });
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to load document");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className={styles.loaderWrapper}>
        <div className={styles.spinner}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <p className={styles.error}>{error}</p>
      </div>
    );
  }

  if (!document) {
    return (
      <div className={styles.container}>
        <p>Document not found</p>
      </div>
    );
  }

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function updateLineItem(index, field, value) {
    setForm((prev) => {
      const lineItems = [...prev.line_items];
      lineItems[index] = { ...lineItems[index], [field]: value };
      return { ...prev, line_items: lineItems };
    });
  }

  function addLineItem() {
    setForm((prev) => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        { description: "", quantity: 1, unit_price: 0, total: 0 },
      ],
    }));
  }

  function removeLineItem(index) {
    setForm((prev) => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index),
    }));
  }

  async function submitUpdate(status) {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage("");

      const payload = {
        document_type: form.document_type || null,
        supplier_name: form.supplier_name || null,
        document_number: form.document_number || null,
        issue_date: form.issue_date || null,
        due_date: form.due_date || null,
        currency: form.currency || null,
        subtotal: Number(form.subtotal) || 0,
        tax: Number(form.tax) || 0,
        total: Number(form.total) || 0,
        line_items: form.line_items.map((item) => ({
          description: item.description || null,
          quantity: Number(item.quantity) || 0,
          unit_price: Number(item.unit_price) || 0,
          total: Number(item.total) || 0,
        })),
      };

      if (status) {
        payload.status = status;
      }

      const res = await fetch(`http://localhost:8000/documents/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const responseData = await res.json();

      if (!res.ok) {
        throw new Error(responseData.detail || "Failed to update document");
      }

      setSuccessMessage(`Document ${responseData.status}`);
      await fetchDocument();
    } catch (err) {
      console.error(err);
      if (err.message?.toLowerCase().includes("validation errors")) {
        setValidationModalMessage(err.message);
        setShowValidationModal(true);
        } else {
        setError(err.message || "Failed to update document");
        }
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className={styles.container}>
      <Link href="/" className={styles.backLink}>
        Back to dashboard
      </Link>
      <h1 className={styles.title}>Document Detail</h1>
      {error && <p className={styles.error}>{error}</p>}
      {successMessage && <p className={styles.success}>{successMessage}</p>}

      {/* BASIC INFO */}
      <div className={styles.card}>
        <div className={styles.infoGrid}>
          <p><span className={styles.label}>ID:</span> {document.id}</p>
          <p><span className={styles.label}>File name:</span> {document.file_name}</p>
          <p><span className={styles.label}>Status:</span> {document.status}</p>
          <label>
            <span className={styles.label}>Document type</span>
            <input
              className={styles.input}
              value={form?.document_type ?? ""}
              onChange={(e) => updateField("document_type", e.target.value)}
            />
          </label>
          <label>
            <span className={styles.label}>Document number</span>
            <input
              className={styles.input}
              value={form?.document_number ?? ""}
              onChange={(e) => updateField("document_number", e.target.value)}
            />
          </label>
          <label>
            <span className={styles.label}>Supplier</span>
            <input
              className={styles.input}
              value={form?.supplier_name ?? ""}
              onChange={(e) => updateField("supplier_name", e.target.value)}
            />
          </label>
          <label>
            <span className={styles.label}>Issue date</span>
            <input
              type="date"
              className={styles.input}
              value={form?.issue_date ?? ""}
              onChange={(e) => updateField("issue_date", e.target.value)}
            />
          </label>
          <label>
            <span className={styles.label}>Due date</span>
            <input
              type="date"
              className={styles.input}
              value={form?.due_date ?? ""}
              onChange={(e) => updateField("due_date", e.target.value)}
            />
          </label>
        </div>
      </div>

      {/* FINANCIAL */}
      <div className={styles.card}>
        <div className={styles.infoGrid}>
          <label>
            <span className={styles.label}>Currency</span>
            <input
              className={styles.input}
              value={form?.currency ?? ""}
              onChange={(e) => updateField("currency", e.target.value)}
            />
          </label>
          <label>
            <span className={styles.label}>Subtotal</span>
            <input
              type="number"
              step="0.01"
              className={styles.input}
              value={form?.subtotal ?? 0}
              onChange={(e) => updateField("subtotal", e.target.value)}
            />
          </label>
          <label>
            <span className={styles.label}>Tax</span>
            <input
              type="number"
              step="0.01"
              className={styles.input}
              value={form?.tax ?? 0}
              onChange={(e) => updateField("tax", e.target.value)}
            />
          </label>
          <label>
            <span className={styles.label}>Total</span>
            <input
              type="number"
              step="0.01"
              className={styles.input}
              value={form?.total ?? 0}
              onChange={(e) => updateField("total", e.target.value)}
            />
          </label>
        </div>
      </div>

      {/* LINE ITEMS */}
      <h2 className={styles.sectionTitle}>Line Items</h2>

      <table className={styles.table}>
        <thead>
          <tr>
            <th>Description</th>
            <th>Qty</th>
            <th>Unit Price</th>
            <th>Total</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {form?.line_items?.length > 0 ? (
            form.line_items.map((item, index) => (
              <tr key={index}>
                <td>
                  <input
                    className={styles.input}
                    value={item.description}
                    onChange={(e) =>
                      updateLineItem(index, "description", e.target.value)
                    }
                  />
                </td>
                <td>
                  <input
                    type="number"
                    className={styles.input}
                    value={item.quantity}
                    onChange={(e) => updateLineItem(index, "quantity", e.target.value)}
                  />
                </td>
                <td>
                  <input
                    type="number"
                    step="0.01"
                    className={styles.input}
                    value={item.unit_price}
                    onChange={(e) =>
                      updateLineItem(index, "unit_price", e.target.value)
                    }
                  />
                </td>
                <td>
                  <input
                    type="number"
                    step="0.01"
                    className={styles.input}
                    value={item.total}
                    onChange={(e) => updateLineItem(index, "total", e.target.value)}
                  />
                </td>
                <td>
                  <button
                    className={styles.buttonDanger}
                    onClick={() => removeLineItem(index)}
                    disabled={saving}
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" style={{ textAlign: "center" }}>
                No line items
              </td>
            </tr>
          )}
        </tbody>
      </table>
      <button className={styles.buttonSecondary} onClick={addLineItem} disabled={saving}>
        Add line item
      </button>

      <h2 className={styles.sectionTitle}>Validation Errors</h2>
      <div className={styles.card}>
        {document.validation_errors?.length > 0 ? (
          <ul>
            {document.validation_errors.map((err, index) => (
              <li key={index}>
                <strong>{err.type}</strong> ({err.field}): {err.message}
              </li>
            ))}
          </ul>
        ) : (
          <p>No validation errors</p>
        )}
      </div>

      <div className={styles.actions}>
        <button
          className={styles.button}
          onClick={() => submitUpdate()}
          disabled={saving}
        >
          {saving ? "Saving..." : "Save corrections"}
        </button>
        <button
          className={styles.button}
          onClick={() => submitUpdate("validated")}
          disabled={saving}
        >
          Confirm
        </button>
        <button
          className={styles.buttonDanger}
          onClick={() => submitUpdate("rejected")}
          disabled={saving}
        >
          Reject
        </button>
      </div>
      {showValidationModal && (
        <div className={styles.modalOverlay}>
            <div className={styles.modal}>
            <h2 className={styles.modalTitle}>Cannot confirm document</h2>

            <p className={styles.modalText}>
                {validationModalMessage}
            </p>

            <div className={styles.modalActions}>
                <button
                className={styles.button}
                onClick={() => setShowValidationModal(false)}
                >
                OK
                </button>
            </div>
            </div>
        </div>
        )}
    </div>
  );
}