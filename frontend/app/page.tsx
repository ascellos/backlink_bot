"use client";
import Image from "next/image";
import { useState , useEffect } from "react";
export default function Home(){
  const [backlinks , setBacklinks] = useState([]);
  const [verifying, setVerifying] = useState(false);
  const [error , setError] = useState(null);

 const fetchBacklinks = async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/backlinks");
    const data = await res.json();
    setBacklinks(data.backlinks);
    setError(null);
  } catch (err) {
    setError("Could not connect to backend. Is the server running?");
  }
};
  useEffect(() => {
  fetchBacklinks();
}, []);

 const verifyBacklinks = async () => {
  setVerifying(true);
  try {
    await fetch("http://127.0.0.1:8000/verify-backlinks", {
      method: "POST",
    });
    await fetchBacklinks();
    setError(null);
  } catch (err) {
    setError("Verification failed. Is the backend running?");
  }
  setVerifying(false);
};
  const getStatusColor = (status) => {
  if (status === "live") return "green";
  if (status === "removed") return "orange";
  if (status === "broken") return "red";
  return "black";
};

 return (
  <div className="p-8">
    <h1 className="text-2xl font-bold mb-4">Backlink Dashboard</h1>

    {error && (
  <p className="text-red-500 mb-4">{error}</p>
)}
    <button
      onClick={verifyBacklinks}
      disabled={verifying}
      className="bg-red-600 text-white px-4 py-2 rounded mb-6"
    >
      {verifying ? "Verifying..." : "Verify All Backlinks"}
    </button>

    <table className="w-full border-collapse">
      <thead>
        <tr className="border-b border-gray-500">
          <th className="text-left p-2">ID</th>
          <th className="text-left p-2">Published URL</th>
          <th className="text-left p-2">Status</th>
        </tr>
      </thead>
      <tbody>
        {backlinks.map((link) => (
          <tr key={link[0]} className="border-b border-gray-700">
            <td className="p-2">{link[0]}</td>
            <td className="p-2">{link[4]}</td>
            <td className="p-2" style={{ color: getStatusColor(link[8]) }}>
              {link[8]}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
}






