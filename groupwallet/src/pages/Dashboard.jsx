import { useEffect, useState } from "react";
import api from "../api/axios";

const iconColor = "text-[#eab308]";

const PayIcon = () => (
  <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
  </svg>
);

const BankIcon = () => (
  <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V10M5 21V10M2 10h20M12 3L2 10h20L12 3zM10 21h4" />
  </svg>
);

const HistoryIcon = () => (
  <svg className={`w-5 h-5 ${iconColor}`} fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h7" />
  </svg>
);

function Dashboard() {
  const [wallet, setWallet] = useState(null);
  const [amount, setAmount] = useState("");
  const [showAddMoney, setShowAddMoney] = useState(false);
  const [showBalance, setShowBalance] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [transactions, setTransactions] = useState([]);

  const token = localStorage.getItem("access");
  
  // Safely grabs username saved during Login/Signup sequence
  const username = localStorage.getItem("username") || "TestingUser";

  // Layout Styles
  const page = "min-h-screen bg-[#f4f4f5] flex flex-col items-center pt-8 px-4 font-sans antialiased text-slate-900";
  const profileRow = "w-full max-w-md flex items-center gap-3 mb-6 px-1";
  const profileCircle = "w-10 h-10 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold uppercase tracking-wider shadow-sm";
  const profileName = "text-sm font-semibold text-slate-800 tracking-tight";
  
  const balanceCard = "w-full max-w-md bg-white border border-slate-200 rounded-2xl p-6 text-slate-900 shadow-sm mb-6";
  const balanceLabel = "text-[11px] font-medium tracking-wider uppercase text-slate-400";
  const balanceAmount = "text-2xl font-semibold tracking-tight text-slate-950 mt-1";
  const viewButton = "text-[11px] bg-slate-100 hover:bg-slate-200 px-3 py-1 rounded-full text-slate-600 font-medium transition-colors cursor-pointer";

  const buttonGrid = "grid grid-cols-3 gap-4 w-full max-w-md mb-6";
  const actionButton = "bg-white border border-slate-200 rounded-2xl p-4 flex flex-col items-center justify-center cursor-pointer hover:border-amber-400 shadow-sm transition-all";
  const iconCircle = "w-11 h-11 bg-amber-50 border border-amber-100 rounded-full flex items-center justify-center mb-2.5";
  const buttonText = "text-[11px] font-medium uppercase text-slate-600 text-center";

  const addMoneyBox = "w-full max-w-md bg-white border border-slate-200 rounded-xl p-4 shadow-sm mb-5";
  const compactInput = "flex-1 border border-slate-200 bg-slate-50 rounded-lg p-2 text-sm outline-none focus:border-amber-400 font-medium text-slate-800";
  const compactBlackButton = "bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium px-4 rounded-lg cursor-pointer transition-colors";
  const compactLabel = "text-[10px] font-medium uppercase tracking-wider text-slate-400 mb-2 block";

  const fetchWallet = async () => {
    try {
      const response = await api.get("/wallets/me/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const personalWallet = response.data.find((w) => w.wallet_type === "PRS");
      setWallet(personalWallet);
    } catch (error) {
      console.log(error);
    }
  };

  const fetchTransactions = async () => {
    try {
      // FIXED: Cleared duplicate '/api' root segment to connect cleanly with your urls.py routing
      const response = await api.get("/transactions/history/", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (Array.isArray(response.data)) {
        setTransactions(response.data);
      } else if (response.data && Array.isArray(response.data.results)) {
        setTransactions(response.data.results);
      }
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    fetchWallet();
    const interval = setInterval(() => {
      fetchWallet();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleAddMoney = async () => {
    if (!amount) return;
    try {
      await api.post(
        "/wallets/add-money/",
        { amount: amount },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAmount("");
      setShowAddMoney(false);
      fetchWallet();

      if (showHistory) {
        fetchTransactions();
      }
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className={page}>
      {/* Top Profile Left Identification Component Row */}
      <div className={profileRow}>
        <div className={profileCircle}>
          {username.substring(0, 2)}
        </div>
        <div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">Welcome</p>
          <p className={profileName}>@{username}</p>
        </div>
      </div>

      {/* Balance Card Section */}
      <div className={balanceCard}>
        <div className="flex items-center justify-between">
          <p className={balanceLabel}>Available Balance</p>
          <button onClick={() => setShowBalance(!showBalance)} className={viewButton}>
            {showBalance ? "Hide" : "View"}
          </button>
        </div>
        <h2 className={balanceAmount}>
          {showBalance ? `₹${wallet ? parseFloat(wallet.balance).toFixed(2) : "0.00"}` : "₹ ••••"}
        </h2>
      </div>

      {/* Action Utilities Buttons Grid */}
      <div className={buttonGrid}>
        <button className={actionButton}>
          <div className={iconCircle}><PayIcon /></div>
          <p className={buttonText}>Pay</p>
        </button>

        <button onClick={() => setShowAddMoney(!showAddMoney)} className={actionButton}>
          <div className={iconCircle}><BankIcon /></div>
          <p className={buttonText}>Bank</p>
        </button>

        <button
          onClick={() => {
            fetchWallet();
            const nextHistoryState = !showHistory;
            setShowHistory(nextHistoryState);
            if (nextHistoryState) {
              fetchTransactions();
            }
          }}
          className={actionButton}
        >
          <div className={iconCircle}><HistoryIcon /></div>
          <p className={buttonText}>History</p>
        </button>
      </div>

      {/* Simulated Deposit View Tray Block */}
      {showAddMoney && (
        <div className={addMoneyBox}>
          <span className={compactLabel}>Simulate Deposit</span>
          <div className="flex gap-2.5">
            <input
              type="number"
              placeholder="Enter amount (₹)"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className={compactInput}
            />
            <button onClick={handleAddMoney} className={compactBlackButton}>
              Add
            </button>
          </div>
        </div>
      )}

      {/* Complete Responsive Transaction History Module */}
      {showHistory && (
        <div className={addMoneyBox}>
          <span className={compactLabel}>Transaction History</span>
          <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
            {transactions.length === 0 ? (
              <div className="text-xs text-slate-400 py-2">No transactions recorded yet.</div>
            ) : (
              transactions.map((tx) => {
                const transactionId = tx.tid || tx.id;
                const rawType = (tx.transaction_type || tx.type || "TRANSFER").toUpperCase();
                const isDeposit = rawType === "DEPOSIT";
                const rawAmount = tx.amount || 0;
                const displayUser = tx.receiver_username || tx.receiver || tx.target_user;
                const rawDate = tx.created_at || tx.timestamp || tx.date;

                return (
                  <div key={transactionId} className="border border-slate-100 rounded-xl p-3 bg-slate-50/70 flex flex-col justify-between">
                    <div className="flex items-center justify-between mb-1.5">
                      <p className="text-sm font-semibold text-slate-800">
                        {isDeposit ? "Deposit to Self" : displayUser ? `@${displayUser}` : "Transfer Out"}
                      </p>
                      <p className={`text-sm font-bold ${isDeposit ? "text-green-600" : "text-red-500"}`}>
                        {isDeposit ? "+" : "-"} ₹{parseFloat(rawAmount).toFixed(2)}
                      </p>
                    </div>

                    <div className="flex items-center justify-between text-[10px] font-medium tracking-wide">
                      <span className={`px-2 py-0.5 rounded-md uppercase text-[9px] font-bold ${
                        isDeposit ? "bg-green-50 text-green-700 border border-green-100" : "bg-red-50 text-red-600 border border-red-100"
                      }`}>
                        {rawType}
                      </span>
                      <p className="text-slate-400">
                        {rawDate ? new Date(rawDate).toLocaleString("en-IN", { timeStyle: "short", dateStyle: "short" }) : "Recent"}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;