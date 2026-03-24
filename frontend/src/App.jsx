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

        <label className={`px-8 py-3 rounded-xl font-medium ${loading?"bg-slate-500 text-slate-300 cursor-not-allowed opacity-50":"bg-white text-black cursor-pointer"}`}>
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
        <div className="mt-12 w-full max-w-6xl grid md:grid-cols-2 gap-6">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
            <h2 className="text-xl font-semibold mb-4">OCR Text</h2>
            <pre className="whitespace-pre-wrap text-sm text-slate-300">
              {result.ocr_text}
            </pre>
          </div>

          <div className="space-y-4">
            {result.error_report?.map((item, index) => (
              <div
                key={index}
                className="bg-slate-900 rounded-2xl border border-slate-800 p-5"
              >
                <h3 className="text-lg font-semibold">{item.drug.toUpperCase()}</h3>

                <p className="mt-2">
                  <span className="font-medium">Issue:</span> {item.issue}
                </p>

                <p>
                  <span className="font-medium">Severity:</span> {item.severity}
                </p>

                <p className="text-slate-300 mt-2">{item.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
