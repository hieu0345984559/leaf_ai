import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, Eye, EyeOff, Lock, Mail, UserPlus, Loader2, CheckCircle2, Sparkles } from 'lucide-react';
import { apiRegister } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';
import { showToast } from '../components/Toast';

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirmation, setPasswordConfirmation] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email || !password || !passwordConfirmation) {
      showToast('error', 'Vui lòng điền đầy đủ tất cả các trường thông tin.');
      return;
    }
    if (password.length < 8) {
      showToast('error', 'Mật khẩu phải có độ dài tối thiểu 8 ký tự.');
      return;
    }
    if (password !== passwordConfirmation) {
      showToast('error', 'Mật khẩu xác nhận không trùng khớp.');
      return;
    }

    setLoading(true);
    try {
      const res = await apiRegister(email, password, passwordConfirmation);
      login(res.access_token, res.user);
      showToast('success', 'Tạo tài khoản thành công! Chào mừng bạn đến với LEAF_AI.');
      navigate('/dashboard');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.';
      showToast('error', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-transparent flex items-center justify-center p-4 sm:p-6 lg:p-8 font-['DM_Sans']">
      <div className="w-full max-w-4xl bg-white/92 backdrop-blur-xl rounded-3xl border border-[#E2EFE7] shadow-2xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 animate-in fade-in zoom-in-95 duration-200">
        {/* Left Side: Brand & Value Prop */}
        <div className="lg:col-span-5 bg-gradient-to-br from-[#14532D] via-[#15803D] to-[#047857] text-white p-8 sm:p-10 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-400/10 rounded-full blur-2xl pointer-events-none -mr-16 -mt-16" />
          <div className="absolute bottom-0 left-0 w-52 h-52 bg-emerald-900/30 rounded-full blur-xl pointer-events-none -ml-12 -mb-12" />

          <div className="relative z-10">
            <div className="inline-flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/15 backdrop-blur-md border border-white/25 flex items-center justify-center text-white shadow-sm">
                <Leaf className="w-5 h-5 text-emerald-200" />
              </div>
              <div>
                <span className="font-extrabold text-lg tracking-tight font-['Space_Grotesk']">
                  LEAF_AI
                </span>
                <span className="block text-[10px] tracking-wider uppercase text-emerald-200/80 font-bold">
                  Thị Giác Nông Học
                </span>
              </div>
            </div>

            <div className="mt-12 space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-semibold text-emerald-100 border border-white/15">
                <Sparkles size={13} className="text-amber-300" />
                <span>Cùng Nhà Nông Toàn Cầu</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight font-['Space_Grotesk'] leading-tight">
                Bảo vệ đồi chè trước khi dịch bệnh lây lan diện rộng.
              </h2>
              <p className="text-xs sm:text-sm text-emerald-100/90 leading-relaxed pt-1">
                Truy cập tức thì công nghệ phát hiện bệnh hại lá chè, đo lường mức độ nghiêm trọng và lộ trình điều trị chuyên sâu.
              </p>
            </div>
          </div>

          <div className="relative z-10 pt-8 border-t border-white/15 space-y-2 text-xs text-emerald-100 font-medium">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={15} className="text-emerald-300 shrink-0" />
              <span>Truy Cập Hoàn Toàn Miễn Phí</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 size={15} className="text-emerald-300 shrink-0" />
              <span>Lưu Trữ Lịch Sử Chẩn Đoán Lâu Dài</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 size={15} className="text-emerald-300 shrink-0" />
              <span>Tương Thích Thiết Bị Di Động & Camera Thực Địa</span>
            </div>
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="lg:col-span-7 p-8 sm:p-12 flex flex-col justify-center">
          <div className="max-w-md mx-auto w-full">
            <div className="mb-8">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0F172A] tracking-tight font-['Space_Grotesk']">
                Tạo Tài Khoản
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Đăng ký để bắt đầu quét chẩn đoán lá chè và tra cứu phác đồ điều trị.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <Mail size={14} className="text-[#15803D]" />
                  Địa Chỉ Email
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="kysu@nongnghiep.vn"
                  className="input-clean"
                  autoComplete="email"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <Lock size={14} className="text-[#15803D]" />
                  Mật Khẩu (tối thiểu 8 ký tự)
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="input-clean pr-11"
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiển thị mật khẩu'}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 transition-colors cursor-pointer"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <CheckCircle2 size={14} className="text-[#15803D]" />
                  Xác Nhận Mật Khẩu
                </label>
                <input
                  type="password"
                  required
                  value={passwordConfirmation}
                  onChange={(e) => setPasswordConfirmation(e.target.value)}
                  placeholder="••••••••"
                  className="input-clean"
                  autoComplete="new-password"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary mt-4 py-3 text-sm font-semibold justify-center"
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Đang Tạo Tài Khoản...</span>
                  </>
                ) : (
                  <>
                    <UserPlus size={16} />
                    <span>Đăng Ký Tài Khoản</span>
                  </>
                )}
              </button>
            </form>

            <div className="mt-8 pt-6 border-t border-[#E2EFE7] text-center">
              <p className="text-xs sm:text-sm text-slate-600">
                Đã có tài khoản?{' '}
                <Link
                  to="/login"
                  className="font-bold text-[#15803D] hover:text-[#166534] underline underline-offset-4"
                >
                  Đăng nhập tại đây
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
