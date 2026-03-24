import { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);

    if (selectedFile) {
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const response = await fetch(
        "https://shubham879-trocrapi.hf.space/process-image",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center p-8">
      <h1 className="text-4xl font-bold">Prescription Error Detection</h1>

      <p className="text-slate-400 mt-2 mb-10 text-center">
        Upload a prescription image for OCR and medical safety analysis
      </p>

      <div className="w-full max-w-md border-2 border-slate-400 rounded-3xl bg-slate-900 p-8 flex flex-col items-center gap-6">
        <div className="w-48 h-48 border border-slate-700 rounded-2xl flex items-center justify-center bg-slate-800">
          {preview ? (
            <img
              src={preview}
              alt="Preview"
              className="w-full h-full object-cover rounded-2xl"
            />
          ) : (
            <span className="text-slate-500">Preview</span>
          )}
        </div>

        <label
          className={`px-8 py-3 rounded-xl font-medium ${
            loading
              ? "bg-slate-500 text-slate-300 cursor-not-allowed opacity-50"
              : "bg-white text-black cursor-pointer"
          }`}
        >
          Select Image
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
            disabled={loading}
          />
        </label>

        <button
          onClick={handleUpload}
          disabled={loading}
          className="px-8 py-3 rounded-xl bg-white text-black font-medium disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze Prescription"}
        </button>
      </div>

      {result && (
        <div className="mt-12 w-full max-w-6xl grid md:grid-cols-2 gap-6 items-start">
          
          {/* OCR TEXT CARD */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 self-start">
            <h2 className="text-xl font-semibold mb-4">OCR Text</h2>
            <pre className="whitespace-pre-wrap text-sm text-slate-300 break-words">
              {result.ocr_text}
            </pre>
          </div>

          {/* ERROR REPORT */}
          <div className="space-y-5">
            {result.error_report?.map((item, index) => (
              <div
                key={index}
                className="bg-slate-900 rounded-2xl border border-slate-800 p-5 hover:border-slate-600 transition-all"
              >
                {/* Header Row */}
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold tracking-wide">
                    {item.drug.toUpperCase()}
                  </h3>

                  <span
                    className={`px-3 py-1 text-xs rounded-full font-medium ${
                      item.severity === "High"
                        ? "bg-red-500/20 text-red-400"
                        : item.severity === "Medium"
                        ? "bg-yellow-500/20 text-yellow-400"
                        : "bg-green-500/20 text-green-400"
                    }`}
                  >
                    {item.severity}
                  </span>
                </div>

                {/* Issue */}
                <p className="mt-3 text-sm">
                  <span className="text-slate-400">Issue:</span>{" "}
                  <span className="text-white font-medium">{item.issue}</span>
                </p>

                {/* Divider */}
                <div className="h-px bg-slate-800 my-3"></div>

                {/* Explanation */}
                <p className="text-slate-300 text-sm leading-relaxed">
                  {item.explanation}
                </p>
              </div>
            ))}
          </div>

        </div>
      )}
    </div>
  );
}