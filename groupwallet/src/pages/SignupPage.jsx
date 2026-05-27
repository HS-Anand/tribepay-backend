import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/axios";

function SignupPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [pin, setPin] = useState("");
  const [confirmPin, setConfirmPin] = useState("");

  const navigate = useNavigate();

  // Premium Slate-Tinted Minimalist Layout Styles
  const page =
    "min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col items-center justify-center py-12 px-4 font-sans antialiased";

  const brandHeading =
    "text-3xl font-semibold tracking-tight text-slate-900 mb-8";

  const card =
    "w-full max-w-md bg-white border border-slate-200 rounded-2xl p-8 shadow-sm";

  const label =
    "block mb-2 text-xs font-medium tracking-wide uppercase text-slate-400";

  const input =
    "w-full border rounded-lg p-3.5 placeholder-slate-400 outline-none transition-colors font-medium text-sm border-slate-200 bg-slate-50 text-slate-900 focus:border-amber-400";

  const signupButton =
    "w-full bg-slate-900 hover:bg-slate-800 text-white p-3.5 rounded-lg font-medium text-sm transition-colors mt-2 cursor-pointer shadow-sm";

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!/^\d{6}$/.test(pin)) {
      alert("PIN must be exactly 6 digits.");
      return;
    }

    if (pin !== confirmPin) {
      alert("PINs do not match.");
      return;
    }

    const generatedUsername = `${firstName}${lastName}${phoneNumber}`.toLowerCase().replace(/\s+/g, "");

    try {
      await api.post("/api/auth/signup/", {
        username: generatedUsername,
        first_name: firstName,
        last_name: lastName,
        phone_number: phoneNumber,
        password: pin,
        confirm_password: confirmPin,
      });

      alert("Account created successfully.");
      navigate("/login");
    } catch (error) {
      if (error.response && error.response.data) {
        console.log(error.response.data);
      } else {
        console.log(error);
      }
      alert("Signup failed.");
    }
  };

  return (
    <div className={page}>
      <h1 className={brandHeading}>PoolPay</h1>

      <div className={card}>
        <h2 className="text-lg font-semibold tracking-tight text-slate-900 mb-6">
          Create Account
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={label}>First Name</label>
              <input
                type="text"
                placeholder="First Name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className={input}
                required
              />
            </div>

            <div>
              <label className={label}>Last Name</label>
              <input
                type="text"
                placeholder="Last Name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className={input}
                required
              />
            </div>
          </div>

          <div>
            <label className={label}>Phone Number</label>
            <input
              type="text"
              placeholder="Enter phone number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className={input}
              required
            />
          </div>

          <div>
            <label className={label}>6-Digit PIN</label>
            <input
              type="password"
              maxLength="6"
              placeholder="Enter PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
              className={input}
              required
            />
          </div>

          <div>
            <label className={label}>Confirm PIN</label>
            <input
              type="password"
              maxLength="6"
              placeholder="Confirm PIN"
              value={confirmPin}
              onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, ""))}
              className={input}
              required
            />
          </div>

          <button type="submit" className={signupButton}>
            Initialize Wallet
          </button>
        </form>

        <p className="mt-6 text-sm text-center text-slate-500">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-amber-600 hover:text-amber-500 transition-colors">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}

export default SignupPage;