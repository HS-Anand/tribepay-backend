import {
  useState,
  useMemo,
  useEffect,
} from "react";

function Dashboard() {
  const [showBalance, setShowBalance] =
    useState(false);

  const [wallet, setWallet] =
    useState(null);

  // Step 1: Added transaction array state
  const [transactions, setTransactions] =
    useState([]);

  const [addAmount, setAddAmount] =
    useState("");

  const [
    receiverWalletId,
    setReceiverWalletId,
  ] = useState("");

  const [sendAmount, setSendAmount] =
    useState("");

  const balance =
    wallet?.balance || 0;

  const fullName =
    localStorage.getItem("mock_name") ||
    "Tribe User";

  const phone =
    localStorage.getItem("mock_phone") ||
    "9876543210";

  const initials = useMemo(() => {
    return fullName
      .split(" ")
      .map((n) => n[0])
      .join("")
      .slice(0, 2)
      .toUpperCase();
  }, [fullName]);

  const fetchWallet = async () => {
    try {
      const token =
        localStorage.getItem("access");

      const response = await fetch(
        "http://127.0.0.1:8000/wallets/me/",
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

      const data =
        await response.json();

      console.log(
        "WALLET RESPONSE:",
        data
      );

      if (Array.isArray(data)) {
        setWallet(data[0]);
      }
    } catch (err) {
      console.log(
        "WALLET ERROR:",
        err
      );
    }
  };

  // Step 2: Added fetchTransactions function
  const fetchTransactions = async () => {
    try {
      const token =
        localStorage.getItem("access");

      const response = await fetch(
        "http://127.0.0.1:8000/api/transactions/history/",
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

      const data =
        await response.json();

      console.log(
        "TRANSACTION RESPONSE:",
        data
      );

      if (Array.isArray(data)) {
        setTransactions(data);
      }
    } catch (err) {
      console.log(
        "TRANSACTION ERROR:",
        err
      );
    }
  };

  const handleAddMoney = async () => {
    try {
      const token =
        localStorage.getItem("access");

      const response = await fetch(
        "http://127.0.0.1:8000/wallets/add-money/",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${token}`,
          },

          body: JSON.stringify({
            amount: addAmount,
          }),
        }
      );

      const data =
        await response.json();

      console.log(
        "ADD MONEY RESPONSE:",
        data
      );

      if (!response.ok) {
        throw new Error(
          JSON.stringify(data)
        );
      }

      setAddAmount("");
      fetchWallet();
      
      // Step 4: Refresh history after adding money
      fetchTransactions();
      
      alert("Money added");
    } catch (err) {
      console.log(err);
      alert(
        err.message ||
          "Add money failed"
      );
    }
  };

  const handleTransfer = async () => {
    try {
      const token =
        localStorage.getItem("access");

      const response = await fetch(
        "http://127.0.0.1:8000/api/transactions/transfer/",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${token}`,
          },

          body: JSON.stringify({
            sender_wallet_id:
              wallet?.wid,

            receiver_wallet_id:
              receiverWalletId,

            amount: sendAmount,
          }),
        }
      );

      const data =
        await response.json();

      console.log(
        "TRANSFER RESPONSE:",
        data
      );

      if (!response.ok) {
        throw new Error(
          JSON.stringify(data)
        );
      }

      setReceiverWalletId("");
      setSendAmount("");
      fetchWallet();
      
      // Step 5: Refresh history after successful transfer
      fetchTransactions();
      
      alert("Transfer successful");
    } catch (err) {
      console.log(err);
      alert(
        err.message ||
          "Transfer failed"
      );
    }
  };

  // Step 3: Updated useEffect lifecycle hooks to initialize wallet and ledger lists
  useEffect(() => {
    fetchWallet();
    fetchTransactions();

    const interval = setInterval(() => {
      fetchWallet();
      fetchTransactions();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const page =
    "min-h-screen bg-[#f8fafc] text-slate-900 px-4 py-8 flex justify-center font-sans antialiased";

  const wrapper =
    "w-full max-w-md";

  const balanceCard =
    "bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-6";

  const actionCard =
    "bg-white border border-slate-200 rounded-2xl p-4 shadow-sm hover:border-amber-300 transition cursor-pointer";

  const sectionCard =
    "bg-white border border-slate-200 rounded-2xl p-5 shadow-sm";

  const input =
    "w-full border border-slate-300 rounded-lg px-4 py-3 outline-none focus:border-amber-400 bg-slate-50";

  const button =
    "w-full bg-slate-900 hover:bg-slate-800 text-white rounded-lg py-3 font-medium transition";

  return (
    <div className={page}>
      <div className={wrapper}>

        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">
              TribePay
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              {phone}
            </p>
          </div>
          <div className="w-12 h-12 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center font-semibold">
            {initials}
          </div>
        </div>

        <div className={balanceCard}>
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Available Balance
            </p>
            <button
              onClick={() => setShowBalance(!showBalance)}
              className="text-xs bg-slate-100 px-3 py-1 rounded-full"
            >
              {showBalance ? "Hide" : "Show"}
            </button>
          </div>
          <h2 className="text-3xl font-bold text-slate-900 mt-3">
            {showBalance
              ? `₹${Number(balance).toFixed(2)}`
              : "₹••••"}
          </h2>
          <p className="text-xs text-slate-400 mt-2">
            Personal Wallet
          </p>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className={actionCard}>
            <p className="font-semibold text-slate-800">Pay</p>
            <p className="text-xs text-slate-500 mt-1">Send money</p>
          </div>
          <div className={actionCard}>
            <p className="font-semibold text-slate-800">Add</p>
            <p className="text-xs text-slate-500 mt-1">Add money</p>
          </div>
          <div className={actionCard}>
            <p className="font-semibold text-slate-800">History</p>
            <p className="text-xs text-slate-500 mt-1">Transactions</p>
          </div>
        </div>

        <div className={`${sectionCard} mb-5`}>
          <h3 className="font-semibold text-slate-900 mb-4">
            Add Money
          </h3>
          <div className="space-y-4">
            <input
              type="number"
              placeholder="Enter amount"
              value={addAmount}
              onChange={(e) => setAddAmount(e.target.value)}
              className={input}
            />
            <button onClick={handleAddMoney} className={button}>
              Add Money
            </button>
          </div>
        </div>

        <div className={`${sectionCard} mb-5`}>
          <h3 className="font-semibold text-slate-900 mb-4">
            Send Money
          </h3>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Receiver Wallet ID"
              value={receiverWalletId}
              onChange={(e) => setReceiverWalletId(e.target.value)}
              className={input}
            />
            <input
              type="number"
              placeholder="Amount"
              value={sendAmount}
              onChange={(e) => setSendAmount(e.target.value)}
              className={input}
            />
            <button onClick={handleTransfer} className={button}>
              Send Money
            </button>
          </div>
        </div>

        <div className={sectionCard}>
          <h3 className="font-semibold text-slate-900 mb-4">
            Recent Transactions
          </h3>
          
          {/* Step 6: Replaced hardcoded templates with dynamic loop structures */}
          <div className="space-y-3">
            {transactions.length === 0 ? (
              <p className="text-sm text-slate-500">
                No transactions yet
              </p>
            ) : (
              transactions.map((tx, index) => (
                <div
                  key={index}
                  className="border border-slate-200 rounded-xl p-4"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-slate-800">
                        {tx.transaction_type || "Transaction"}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        {tx.created_at
                          ? new Date(tx.created_at).toLocaleString()
                          : "Recent"}
                      </p>
                    </div>
                    <p className="font-bold text-slate-900">
                      ₹{tx.amount}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

export default Dashboard;