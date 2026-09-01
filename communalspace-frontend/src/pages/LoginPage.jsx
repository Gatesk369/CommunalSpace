import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "motion/react";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[radial-gradient(circle,theme(colors.cs-orange)_0%,theme(colors.cs-coral)_30%,theme(colors.cs-magenta)_65%,theme(colors.cs-purple)_100%)]">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-full w-[420px] h-[420px] flex flex-col items-center justify-center p-10"
      >
        <h1 className="text-cs-red text-2xl font-extrabold mb-6">
          Welcome Back
        </h1>

        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-3">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border border-cs-line rounded-full px-4 py-2 text-sm outline-none focus:border-cs-orange"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="border border-cs-line rounded-full px-4 py-2 text-sm outline-none focus:border-cs-orange"
          />

          {error && <p className="text-cs-red text-xs text-center">{error}</p>}

          <Link
            to="/forgot-password"
            className="text-xs underline text-center text-cs-ink"
          >
            Forgot Password?
          </Link>

          <motion.button
            whileTap={{ scale: 0.96 }}
            type="submit"
            className="bg-cs-orange text-white font-bold rounded-full py-2 mt-2"
          >
            Log In
          </motion.button>
        </form>

        <p className="text-xs mt-6">
          New to Communal Space?{" "}
          <Link to="/signup" className="font-bold underline">
            Sign up
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
