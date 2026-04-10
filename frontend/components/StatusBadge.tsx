type Props = {
  status: string;
};

export default function StatusBadge({ status }: Props) {
  const base = "inline-flex rounded-full px-3 py-1 text-sm font-medium";

  const styles: Record<string, string> = {
    applied: "bg-blue-100 text-blue-700",
    interview: "bg-yellow-100 text-yellow-700",
    offer: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
  };

  return (
    <span className={`${base} ${styles[status] || "bg-slate-100 text-slate-700"}`}>
      {status}
    </span>
  );
}