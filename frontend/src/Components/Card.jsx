export default function Card({ drug, issue, severity, explanation }) {
  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 hover:border-slate-600 transition-all hover:shadow-lg hover:shadow-purple-500/10">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold tracking-wide">
          {drug.toUpperCase()}
        </h3>

        <span
          className={`px-3 py-1 text-xs rounded-full font-medium ${
            severity === "High"
              ? "bg-red-500/20 text-red-400"
              : severity === "Medium"
              ? "bg-yellow-500/20 text-yellow-400"
              : "bg-green-500/20 text-green-400"
          }`}
        >
          {severity}
        </span>
      </div>

      {/* Issue */}
      <p className="mt-3 text-sm">
        <span className="text-slate-400">Issue:</span>{" "}
        <span className="text-white font-medium">{issue}</span>
      </p>

      {/* Divider */}
      <div className="h-px bg-slate-800 my-3"></div>

      {/* Explanation */}
      <p className="text-slate-300 text-sm leading-relaxed">
        {explanation}
      </p>
    </div>
  );
}