import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/axios";

function LoginPage() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [pin, setPin] = useState("");
  const navigate = useNavigate();

  const page = 
    "min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col items-center justify-center px-4 font-sans antialiased";

  const brandHeading = 
    "text-3xl font-semibold tracking-tight text-slate-900 mb-8";

  const cardContainer = 
    "w-full max-w-md rounded-2xl p-8 border bg-white border-slate-200 shadow-sm flex flex-col relative overflow-hidden";

  const formLabel = 
    "block mb-2 text-xs font-medium tracking-wide uppercase text-slate-400";

  const formInput = 
    "w-full border rounded-lg p-3.5 placeholder-slate-400 outline-none transition-colors font-medium text-sm border-slate-200 bg-slate-50 text-slate-900 focus:border-amber-400";

  const loginButton = 
    "w-full p-3.5 rounded-lg font-medium text-sm transition-colors cursor-pointer shadow-sm mt-2 bg-slate-900 hover:bg-slate-800 text-white";

  const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const response = await api.post("/api/auth/login/", {
      phone_number: phoneNumber,
      password: pin,
    });

    // Save tokens
    localStorage.setItem("access", response.data.access);
    localStorage.setItem("refresh", response.data.refresh);
    
    // CRITICAL: Save the username returned by your DRF backend!
    // (Ensure your backend serializer sends this field, e.g., response.data.username)
    localStorage.setItem("username", response.data.username || phoneNumber);

    navigate("/dashboard");
  } catch (error) {
    console.log(error);
    alert("Verification failed. Try again.");
  }
};

  return (
    <div className={page}>
      <h1 className={brandHeading}>PoolPay</h1>

      <div className={cardContainer}>
        <h2 className="text-lg font-semibold tracking-tight text-slate-900 mb-6">
          Access Ledger
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className={formLabel}>Phone Number</label>
            <input
              type="text"
              placeholder="Enter phone number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className={formInput}
              required
            />
          </div>

          <div>
            <label className={formLabel}>Security PIN</label>
            <input
              type="password"
              placeholder="Enter PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              className={formInput}
              required
            />
          </div>

          <button type="submit" className={loginButton}>
            Verify Identity
          </button>
        </form>

        <p className="mt-6 text-sm text-center text-slate-500">
          Don't have an account?{" "}
          <Link to="/signup" className="font-medium text-amber-600 hover:text-amber-500 transition-colors">
            Get Started
          </Link>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;