import type { Application } from "@/types/application";
import StatusBadge from "@/components/StatusBadge";

type Props = {
  application: Application;
  onStatusChange: (id: number, status: string) => Promise<void>;
};

export default function ApplicationCard({ application, onStatusChange }: Props) {
  return (
    <div className="rounded-xl bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">
            {application.title}
          </h3>
          <p className="text-slate-600">
            {application.company}
            {application.location ? ` • ${application.location}` : ""}
          </p>
          <p className="mt-1 text-sm text-slate-500">
            Source: {application.source || "N/A"}
          </p>
        </div>

        <StatusBadge status={application.status} />
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {["applied", "interview", "offer", "rejected"].map((status) => (
          <button
            key={status}
            onClick={() => onStatusChange(application.id, status)}
            className="rounded-lg border px-3 py-2 text-sm hover:bg-slate-50"
          >
            Mark {status}
          </button>
        ))}
      </div>

      {application.notes && (
        <p className="mt-4 text-sm text-slate-600">{application.notes}</p>
      )}
    </div>
  );
}