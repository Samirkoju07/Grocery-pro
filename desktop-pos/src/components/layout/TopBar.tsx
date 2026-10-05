import { Bell, User } from "lucide-react";

export function TopBar() {
  return (
    <header className="flex h-14 items-center justify-between border-b border-gray-200 bg-white px-6 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-gray-600">
          Grocery POS
        </span>
      </div>
      <div className="flex items-center gap-3">
        <button className="relative rounded-full p-2 text-gray-500 hover:bg-gray-100">
          <Bell className="h-5 w-5" />
        </button>
        <button className="flex items-center gap-2 rounded-full border border-gray-200 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50">
          <User className="h-4 w-4" />
          <span>Admin</span>
        </button>
      </div>
    </header>
  );
}
