"use client";

import { useState } from "react";

type Props = {
  onSubmit: (payload: {
    job_id: string;
    company: string;
    title: string;
    location?: string;
    source?: string;
    status?: string;
    notes?: string;
  }) => Promise<void>;
};

export default function AddApplicationForm({ onSubmit }: Props) {
  const [form, setForm] = useState({
    job_id: "",
    company: "",
    title: "",
    location: "",
    source: "",
    status: "applied",
    notes: "",
  });

  const [submitting, setSubmitting] = useState(false);

  function updateField(name: string, value: string) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);

    try {
      await onSubmit(form);
      setForm({
        job_id: "",
        company: "",
        title: "",
        location: "",
        source: "",
        status: "applied",
        notes: "",
      });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-xl font-semibold text-slate-900">Add Application</h2>

      <div className="grid gap-4 md:grid-cols-2">
        <input
          className="rounded-lg border p-3"
          placeholder="Job ID"
          value={form.job_id}
          onChange={(e) => updateField("job_id", e.target.value)}
          required
        />
        <input
          className="rounded-lg border p-3"
          placeholder="Company"
          value={form.company}
          onChange={(e) => updateField("company", e.target.value)}
          required
        />
        <input
          className="rounded-lg border p-3"
          placeholder="Title"
          value={form.title}
          onChange={(e) => updateField("title", e.target.value)}
          required
        />
        <input
          className="rounded-lg border p-3"
          placeholder="Location"
          value={form.location}
          onChange={(e) => updateField("location", e.target.value)}
        />
        <input
          className="rounded-lg border p-3"
          placeholder="Source"
          value={form.source}
          onChange={(e) => updateField("source", e.target.value)}
        />
        <select
          className="rounded-lg border p-3"
          value={form.status}
          onChange={(e) => updateField("status", e.target.value)}
        >
          <option value="applied">Applied</option>
          <option value="interview">Interview</option>
          <option value="offer">Offer</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      <textarea
        className="mt-4 min-h-28 w-full rounded-lg border p-3"
        placeholder="Notes"
        value={form.notes}
        onChange={(e) => updateField("notes", e.target.value)}
      />

      <button
        type="submit"
        disabled={submitting}
        className="mt-4 rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
      >
        {submitting ? "Saving..." : "Add Application"}
      </button>
    </form>
  );
}