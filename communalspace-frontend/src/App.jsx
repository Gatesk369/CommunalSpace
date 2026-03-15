import { useState } from "react";
import axios from "axios";

function App() {
  const [spaces, setSpaces] = useState([]);

  const fetchSpaces = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/spaces/");
      setSpaces(response.data);
    } catch (error) {
      console.error("Backend connection failed!", error);
    }
  };
  fetchSpaces();

  return (
    // bg-slate-50: Very light gray background
    // min-h-screen: Ensures background covers the whole page
    <div className="min-h-screen bg-slate-50 p-6 md:p-12">
      <header className="max-w-6xl mx-auto mb-12">
        <h1 className="text-5xl font-black text-slate-900 tracking-tight">
          Communal<span className="text-indigo-600">Space</span>
        </h1>
        <p className="text-slate-500 mt-2 text-lg">
          Your neighborhood, digitally connected.
        </p>
      </header>

      {/* Grid system: 1 col on mobile, 2 on tablet, 3 on desktop */}
      <main className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {spaces.map((space) => (
          <div
            key={space.id}
            className="group bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-xl hover:border-indigo-200 transition-all duration-300"
          >
            {/* Type Badge */}
            <span className="inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest bg-indigo-50 text-indigo-600">
              {space.location_type}
            </span>

            <h2 className="text-2xl font-bold text-slate-800 mt-4 group-hover:text-indigo-600 transition-colors">
              {space.name}
            </h2>

            <p className="text-slate-600 mt-3 line-clamp-3 text-sm leading-relaxed">
              {space.description}
            </p>

            <div className="mt-6 pt-6 border-t border-slate-100">
              <button className="w-full bg-slate-900 text-white py-3 rounded-xl font-semibold hover:bg-indigo-600 transition-colors shadow-lg shadow-slate-200 hover:shadow-indigo-200">
                View Space Details
              </button>
            </div>
          </div>
        ))}
      </main>
    </div>
  );
}

export default App;
