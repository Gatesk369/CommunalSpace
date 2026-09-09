export default function MessagesBar({ unreadCount = 0 }) {
  return (
    <div className="drop-shadow-lg lg:fixed lg:bottom-8 lg:right-8 flex items-center justify-between bg-white border-2 border-cs-line rounded-full px-5 py-3">
      <span className="text-sm font-bold pr-8">Messages</span>
      {unreadCount > 0 && (
        <span className="bg-cs-magenta text-white text-xs font-bold w-8 h-8 rounded-full flex items-center justify-center">
          {unreadCount}
        </span>
      )}
    </div>
  );
}
