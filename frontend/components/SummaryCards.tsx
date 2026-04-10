import type { Application } from "@/types/application";

type Props = {
  applications: Application[];
};

export default function SummaryCards({ applications }: Props) {
  const total = applications.length;
  const applied = applications.filter((a) => a.status === "applied").length;
  const interview = applications.filter((a) => a.status === "interview").length;
  const offer = applications.filter((a) => a.status === "offer").length;

  const cards = [
    { label: "Total", value: total },
    { label: "Applied", value: applied },
    { label: "Interviews", value: interview },
    { label: "Offers", value: offer },
  ];

  return (
    <section className="grid gap-4 md:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="rounded-xl bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">{card.label}</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">{card.value}</p>
        </div>
      ))}
    </section>
  );
}