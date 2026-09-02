import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "motion/react";
import { useAuth } from "../context/AuthContext";
import AuthBackground from "../components/AuthBackground";

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
    <AuthBackground>
      <motion.div
        initial={{ scale: 0, opacity: 0, rotate: 0 }}
        animate={{ scale: 1, opacity: 1, rotate: [0, 20] }}
        transition={{
          scale: { duration: 2, delay: 0.6, ease: [1, 0, 0, 1] },
          opacity: { duration: 2, delay: 0.6, ease: [1, 0, 0, 1] },
          rotate: {
            duration: 11,
            repeat: Infinity,
            repeatType: "reverse",
            ease: [0.65, 0, 0.35, 1],
          },
        }}
        className="relative z-10 drop-shadow-[0_0px_20px_rgba(0,0,0,0.3)] bg-white rounded-[50%] w-[700px] h-[780px] flex flex-col items-center justify-center p-10"
      >
        <motion.div
          initial={{ opacity: 0, rotate: 0 }}
          animate={{ opacity: 1, rotate: [0, -20] }}
          transition={{
            opacity: { delay: 2.6, duration: 0.6, ease: "easeOut" },
            rotate: {
              duration: 11,
              repeat: Infinity,
              repeatType: "reverse",
              ease: [0.65, 0, 0.35, 1],
            },
          }}
          className="w-[600px] h-[600px] flex flex-col items-center justify-center p-10"
        >
          <h1 className="text-cs-red text-[72px] font-semibold mb-8">
            Welcome Back
          </h1>

          <form
            onSubmit={handleSubmit}
            className="drop-shadow-md w-[70%] flex flex-col gap-3"
          >
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-white border border-cs-line rounded-full px-4 py-3.5 text-xl outline-none focus:border-cs-orange"
            />

            {error && (
              <p className="text-cs-red text-lg text-center">{error}</p>
            )}

            <Link
              to="/forgot-password"
              className="text-lg underline text-center text-cs-ink"
            >
              Forgot Password?
            </Link>
            <div className="w-full flex items-center justify-center">
              <motion.button
                whileTap={{ scale: 0.96 }}
                type="submit"
                className="w-[80%] bg-cs-orange text-white text-xl font-bold rounded-full py-3.5 mt-2"
              >
                Log In
              </motion.button>
            </div>
          </form>

          <p className="text-lg mt-6">
            New to Communal Space?{" "}
            <Link to="/signup" className="font-bold underline">
              Sign up
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </AuthBackground>
  );
}
