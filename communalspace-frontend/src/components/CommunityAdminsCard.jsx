export default function CommunityAdminsCard({ admins }) {
  return (
    <div className="bg-white border-2 border-cs-line rounded-3xl p-5 mb-6">
      <h2 className="text-base font-bold text-cs-ink mb-3">Community Admins</h2>
      <div className="flex flex-col gap-3">
        {admins.map((admin) => (
          <div
            key={admin.id}
            className="flex items-center gap-3 border-2 border-cs-line rounded-2xl px-3 py-2.5"
          >
            <div className="w-9 h-9 rounded-full bg-cs-magenta flex-shrink-0" />
            <span className="text-sm font-semibold text-cs-ink">
              {admin.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
