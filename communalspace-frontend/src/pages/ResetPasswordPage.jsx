import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { motion } from "motion/react";
import AuthBackground from "../components/AuthBackground";
import { confirmPasswordReset } from "../api/auth";

export default function ResetPasswordPage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    try {
      await confirmPasswordReset(token, password);
      navigate("/login");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <AuthBackground>
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 2, ease: [1, 0, 0, 1] }}
        className="relative z-10 drop-shadow-[0_0px_20px_rgba(0,0,0,0.3)] bg-white rounded-[50%] w-[700px] h-[700px] flex flex-col items-center justify-center p-10 text-center"
      >
        <h1 className="text-cs-red text-[56px] font-semibold mb-6">
          New Password
        </h1>
        <form onSubmit={handleSubmit} className="w-[70%] flex flex-col gap-3">
          <input
            type="password"
            placeholder="New password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
          />
          <input
            type="password"
            placeholder="Confirm new password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
          />
          {error && <p className="text-cs-red text-lg text-center">{error}</p>}
          <motion.button
            whileTap={{ scale: 0.96 }}
            type="submit"
            className="bg-cs-orange text-white text-xl font-bold rounded-full py-3.5 mt-2"
          >
            Reset Password
          </motion.button>
        </form>
        <p className="text-lg mt-6">
          <Link to="/login" className="font-bold underline">
            Back to login
          </Link>
        </p>
      </motion.div>
    </AuthBackground>
  );
}
