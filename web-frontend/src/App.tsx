import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Upload, FileText, Activity, Clock, Download } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const API_URL = 'http://127.0.0.1:8000/api';

const authHeader = {
  headers: {
    'Authorization': 'Basic ' + btoa('admin:password')
  }
};

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [data, setData] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_URL}/history/`, authHeader);
      setHistory(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      setMsg('Uploading...');
      const res = await axios.post(`${API_URL}/upload/`, formData, authHeader);
      setData(res.data);
      setMsg('Upload Successful!');
      fetchHistory();
    } catch (err: any) {
      setMsg('Error: ' + (err.response?.data?.error || err.message));
    }
  };

  const downloadReport = async () => {
    try {
      const res = await axios.get(`${API_URL}/report_pdf/`, { ...authHeader, responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'report.pdf');
      document.body.appendChild(link);
      link.click();
    } catch (e) {
      alert("Failed to download PDF");
    }
  }

  const chartData = data ? {
    labels: Object.keys(data.type_distribution),
    datasets: [
      {
        label: 'Count',
        data: Object.values(data.type_distribution),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
        ],
        borderWidth: 1,
      },
    ],
  } : { labels: [], datasets: [] };

  return (
    <div className="min-h-screen p-8 font-sans text-gray-100">
      <nav className="flex justify-between items-center mb-10 glass p-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Activity className="text-indigo-400" />
          Chemical Equipment Visualizer
        </h1>
        <div className="text-sm opacity-75">v1.0 Hybrid | Admin</div>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Upload Section */}
        <div className="glass p-6 h-fit">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Upload size={20} /> Upload Dataset
          </h2>
          <div className="border-2 border-dashed border-gray-500 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => e.target.files && setFile(e.target.files[0])}
              className="hidden"
              id="fileInput"
            />
            <label htmlFor="fileInput" className="cursor-pointer block">
              <FileText className="mx-auto mb-2 text-gray-400" size={40} />
              <p className="text-sm text-gray-300">
                {file ? file.name : "Click to select CSV"}
              </p>
            </label>
          </div>

          <button
            onClick={handleUpload}
            className="w-full mt-4 btn-primary"
            disabled={!file}
          >
            Analyze Data
          </button>

          {msg && <p className="mt-2 text-center text-sm text-indigo-300">{msg}</p>}
        </div>

        {/* Dashboard Section */}
        <div className="glass p-6 lg:col-span-2">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Dashboard</h2>
            {data && (
              <button onClick={downloadReport} className="flex items-center gap-2 text-sm bg-indigo-500 hover:bg-indigo-600 px-3 py-1 rounded transition">
                <Download size={16} /> PDF Report
              </button>
            )}
          </div>

          {!data ? (
            <div className="flex flex-col items-center justify-center h-64 opacity-50">
              <Activity size={64} />
              <p className="mt-4">Upload data to see analytics</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card title="Total Count" value={data.total_count} />
                <Card title="Avg Flowrate" value={data.avg_flowrate.toFixed(1)} unit="L/h" />
                <Card title="Avg Pressure" value={data.avg_pressure.toFixed(1)} unit="Bar" />
                <Card title="Avg Temp" value={data.avg_temperature.toFixed(1)} unit="°C" />
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div className="bg-black/20 p-4 rounded-lg">
                  <h3 className="mb-2 text-center text-sm font-semibold">Equipment Distribution</h3>
                  <div className="h-64 flex justify-center">
                    <Doughnut data={chartData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }} />
                  </div>
                </div>
                <div className="bg-black/20 p-4 rounded-lg">
                  <h3 className="mb-2 text-center text-sm font-semibold">Count by Type</h3>
                  <div className="h-64">
                    <Bar data={chartData} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* History Section */}
        <div className="glass p-6 lg:col-span-3">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Clock size={20} /> Recent Uploads
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-600 text-gray-400">
                  <th className="p-2">Filename</th>
                  <th className="p-2">Date</th>
                  <th className="p-2">Summary</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={h.id} className="border-b border-gray-700 hover:bg-white/5 transition">
                    <td className="p-2">{h.filename}</td>
                    <td className="p-2 text-sm">{new Date(h.upload_date).toLocaleString()}</td>
                    <td className="p-2 text-sm text-gray-300">
                      Count: {h.summary_data.total_count},
                      Avg T: {h.summary_data.avg_temperature.toFixed(1)}
                    </td>
                  </tr>
                ))}
                {history.length === 0 && (
                  <tr><td colSpan={3} className="p-4 text-center opacity-50">No history found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}

function Card({ title, value, unit }: { title: string, value: any, unit?: string }) {
  return (
    <div className="bg-white/10 p-4 rounded-lg text-center backdrop-blur-sm">
      <p className="text-xs text-gray-400 uppercase tracking-widest">{title}</p>
      <p className="text-2xl font-bold mt-1 text-white">{value} <span className="text-sm font-normal text-gray-400">{unit}</span></p>
    </div>
  );
}

export default App;
