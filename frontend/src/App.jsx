import { useState } from "react";
import Card from "./Components/Card";

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

      {/* Upload Box */}
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

      {/* RESULT SECTION */}
      {result && (
        <div className="mt-12 w-full max-w-6xl space-y-8">

          {/* TOP: OCR + EXPLANATION */}
          <div className="grid md:grid-cols-2 gap-6 items-start">

            {/* OCR TEXT */}
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
              <h2 className="text-xl font-semibold mb-4">OCR Text</h2>
              <pre className="whitespace-pre-wrap text-sm text-slate-300 break-words">
                {result.ocr_text}
              </pre>
            </div>

            {/* USER EXPLANATION */}
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
              <h2 className="text-xl font-semibold mb-4">
                Overall Analysis
              </h2>
              <p className="text-slate-300 leading-relaxed">
                {result.user_explanation}
              </p>
            </div>

          </div>

          {/* BOTTOM: DRUG CARDS */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {result.drug_analysis?.map((item, index) => (
              <Card
                key={index}
                drug={item.drug}
                issue={item.issue}
                severity={item.severity}
                explanation={item.explanation}
              />
            ))}
          </div>

        </div>
      )}
    </div>
  );
}