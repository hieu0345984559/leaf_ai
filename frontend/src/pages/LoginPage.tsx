import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, Eye, EyeOff, Lock, Mail, ArrowRight, Loader2, Sparkles, CheckCircle2 } from 'lucide-react';
import { apiLogin } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';
import { showToast } from '../components/Toast';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      showToast('error', 'Vui lòng cung cấp cả email và mật khẩu.');
      return;
    }

    setLoading(true);
    try {
      const res = await apiLogin(email, password);
      login(res.access_token, res.user);
      showToast('success', `Chào mừng trở lại, ${res.user.email}!`);
      navigate('/dashboard');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Xác thực thất bại. Vui lòng kiểm tra lại thông tin đăng nhập.';
      showToast('error', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-transparent flex items-center justify-center p-4 sm:p-6 lg:p-8 font-['DM_Sans']">
      <div className="w-full max-w-4xl bg-white/92 backdrop-blur-xl rounded-3xl border border-[#E2EFE7] shadow-2xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 animate-in fade-in zoom-in-95 duration-200">
        {/* Left Side: Brand & Value Prop (5 cols on lg) */}
        <div className="lg:col-span-5 bg-gradient-to-br from-[#14532D] via-[#15803D] to-[#047857] text-white p-8 sm:p-10 flex flex-col justify-between relative overflow-hidden">
          {/* Subtle nature circle patterns */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-400/10 rounded-full blur-2xl pointer-events-none -mr-16 -mt-16" />
          <div className="absolute bottom-0 left-0 w-52 h-52 bg-emerald-900/30 rounded-full blur-xl pointer-events-none -ml-12 -mb-12" />

          {/* Top Logo */}
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
                <span>Bệnh Học Cây Chè Tiên Tiến</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight font-['Space_Grotesk'] leading-tight">
                Đồng hành cùng người trồng chè với AI chẩn đoán chính xác.
              </h2>
              <p className="text-xs sm:text-sm text-emerald-100/90 leading-relaxed pt-1">
                Định vị bệnh hại lá theo thời gian thực, hộp bao quanh chuẩn xác từng pixel và phác đồ quản lý IPM toàn diện.
              </p>
            </div>
          </div>

          {/* Feature list pills */}
          <div className="relative z-10 pt-8 border-t border-white/15 space-y-2 text-xs text-emerald-100 font-medium">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={15} className="text-emerald-300 shrink-0" />
              <span>Phát Hiện Đối Tượng YOLOv11</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 size={15} className="text-emerald-300 shrink-0" />
              <span>Độ Tin Cậy Được Hiệu Chuẩn</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 size={15} className="text-emerald-300 shrink-0" />
              <span>Lộ Trình Điều Trị Tích Hợp</span>
            </div>
          </div>
        </div>

        {/* Right Side: Form (7 cols on lg) */}
        <div className="lg:col-span-7 p-8 sm:p-12 flex flex-col justify-center">
          <div className="max-w-md mx-auto w-full">
            <div className="mb-8">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0F172A] tracking-tight font-['Space_Grotesk']">
                Đăng Nhập
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Truy cập không gian làm việc và hồ sơ chẩn đoán bệnh học cây chè của bạn.
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
                  placeholder="nongdan@nongnghiep.vn"
                  className="input-clean"
                  autoComplete="email"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <Lock size={14} className="text-[#15803D]" />
                  Mật Khẩu
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="input-clean pr-11"
                    autoComplete="current-password"
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

              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary mt-4 py-3 text-sm font-semibold justify-center"
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Đang Xác Thực Thông Tin...</span>
                  </>
                ) : (
                  <>
                    <span>Đăng Nhập Vào Bảng Điều Khiển</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            <div className="mt-8 pt-6 border-t border-[#E2EFE7] text-center">
              <p className="text-xs sm:text-sm text-slate-600">
                Chưa có tài khoản?{' '}
                <Link
                  to="/register"
                  className="font-bold text-[#15803D] hover:text-[#166534] underline underline-offset-4"
                >
                  Tạo tài khoản miễn phí
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
